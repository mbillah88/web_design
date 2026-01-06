from django.core.management.base import BaseCommand
from django.db import connections, OperationalError
from django.contrib.auth.hashers import make_password
from django.core.management import call_command
from accounts.models import (
    Role, ModuleGroup, Module, Permission, CustomUser,
    Department, Profile, ActionType
)
from products.models import (
    Category, Brand, Unit, Warranty, PaymentMethod, TransactionType
)
from accounts.constants import MODULE_LAYOUT

class Command(BaseCommand):
    help = "🎯 ফুল সিস্টেম সেটআপ: রোল, ইউজার, প্রোফাইল, মডিউল, গ্রুপ, পারমিশন, সাইডবার, হেডার, মাস্টার ডেটা"

    def handle(self, *args, **kwargs):
        # ✅ 1. DB Connection Check
        try:
            connections['default'].ensure_connection()
            self.stdout.write(self.style.SUCCESS("✅ ডাটাবেজ সংযোগ সফল"))
        except OperationalError:
            self.stdout.write(self.style.ERROR("❌ ডাটাবেজ সংযোগ ব্যর্থ"))
            return

        # ✅ 2. Migrate
        call_command('migrate', interactive=False)
        self.stdout.write(self.style.SUCCESS("✅ মাইগ্রেশন সম্পন্ন"))

        # ✅ 3. ActionTypes
        action_keys = ['access', 'create', 'edit', 'delete']
        action_map = {}
        for i, key in enumerate(action_keys):
            action, _ = ActionType.objects.get_or_create(
                key=key,
                defaults={'name_bn': key.title(), 'order': i}
            )
            action_map[key] = action

        # ✅ 4. SystemAdmin Role
        role, _ = Role.objects.get_or_create(name="SystemAdmin", defaults={"is_protected": True})

        # ✅ 5. Department
        dept, _ = Department.objects.get_or_create(name="Administration", code="ADM")

        # ✅ 6. Admin User
        user, _ = CustomUser.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "is_staff": True,
                "is_superuser": True,
                "role": role,
                "password": make_password("admin123"),
                "is_protected": True
            }
        )

        # ✅ 7. Profile
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.department = dept
        profile.designation = "System Administrator"
        profile.save()

        # ✅ 8. ModuleGroups and Modules
        for group_name, modules in MODULE_LAYOUT.items():
            if not isinstance(modules, dict):
                self.stdout.write(self.style.WARNING(f"⚠️ গ্রুপ '{group_name}' এর modules dict নয়"))
                continue

            group, _ = ModuleGroup.objects.get_or_create(name=group_name)

            for parent_url, config in modules.items():
                config = config or {}
                if not isinstance(config, dict):
                    self.stdout.write(self.style.WARNING(f"⚠️ '{parent_url}' এর config dict নয়"))
                    continue

                parent, _ = Module.objects.get_or_create(
                    url_name=parent_url,
                    defaults={
                        "name": config.get("name", parent_url.split(":")[-1].replace('_', ' ').title()),
                        "label": config.get("label"),
                        "group": group,
                        "icon": config.get("icon", "bi-speedometer"),
                        "is_visible": True,
                        "is_header": config.get("is_header", False),
                        "order": config.get("order", 0)
                    }
                )
                parent.actions.set([action_map['access']])

                for child_url in config.get("children", []):
                    inferred = []
                    if 'add' in child_url: inferred.append('create')
                    if 'edit' in child_url: inferred.append('edit')
                    if 'delete' in child_url: inferred.append('delete')
                    if 'list' in child_url or 'view' in child_url: inferred.append('access')
                    if not inferred: inferred = ['access']

                    child, _ = Module.objects.get_or_create(
                        url_name=child_url,
                        defaults={
                            "name": child_url.replace('_', ' ').title(),
                            "group": group,
                            "parent": parent,
                            "icon": "bi-circle",
                            "is_visible": False,
                            "is_header": False,
                            "order": 0
                        }
                    )
                    child.actions.set([action_map[k] for k in inferred])

        # ✅ 9. Assign Full Permissions to SystemAdmin
        for module in Module.objects.all():
            for action in ActionType.objects.all():
                perm, created = Permission.objects.get_or_create(
                    role=role,
                    module=module,
                    action=action,
                    defaults={'is_allowed': True}
                )
                if not created:
                    perm.is_allowed = True
                    perm.save()

        self.stdout.write(self.style.SUCCESS("✅ SystemAdmin has full access to all modules"))

        # ✅ 10. Seed Master Data
        self.seed_master_data(user)

        self.stdout.write(self.style.SUCCESS("🎉 ফুল সিস্টেম সেটআপ সম্পন্ন ✅"))

    def seed_master_data(self, user):
        # ✅ Categories
        for name in ["Laptop", "Desktop", "RAM", "SSD", "Monitor"]:
            Category.objects.get_or_create(name=name, defaults={"created_by": user})

        # ✅ Brands
        brands = {
            "HP": "USA",
            "Dell": "USA",
            "Lenovo": "China",
            "Transcend": "Taiwan"
        }
        for name, country in brands.items():
            Brand.objects.get_or_create(name=name, defaults={"country": country, "created_by": user})

        # ✅ Units
        unit_names = ["Peaces", "Boxes", "Set", "Gigabyte", "Terabyte"]
        unit_symbols = ["pcs", "box", "set", "GB", "TB"]

        for name, symbol in zip(unit_names, unit_symbols):
            Unit.objects.get_or_create(
                name=name,
                symbol=symbol,
                created_by=user
            )


        # ✅ Warranties
        Warranty.objects.get_or_create(
            name="3 Years Seller Warranty",
            type="seller",
            duration_value=3,
            duration_unit="years",
            is_active=True,
            created_by=user
        )
        Warranty.objects.get_or_create(
            name="1 Year Manufacturer Warranty",
            type="manufacturer",
            duration_value=1,
            duration_unit="years",
            is_active=True,
            created_by=user
        )
        Warranty.objects.get_or_create(
            name="No Warranty",
            type="none",
            duration_value=0,
            duration_unit="days",
            is_active=True,
            created_by=user
        )
        Warranty.objects.get_or_create(
            name="Lifetime Warranty",
            type="lifetime",
            duration_value=0,
            duration_unit="days",
            is_lifetime=True,
            is_active=True,
            created_by=user
        )

        # ✅ Payment Methods
        payment_methods = [
            {"name": "Cash", "description": "Cash payment"},
            {"name": "Card", "description": "Credit/Debit card"},
            {"name": "bKash", "description": "bKash mobile payment"},
            {"name": "Nagad", "description": "Nagad mobile payment"},
            {"name": "Rocket", "description": "Rocket mobile payment"},
            {"name": "Bank Transfer", "description": "Direct bank transfer"},
            {"name": "Cheque", "description": "Cheque payment"},
        ]
        for method in payment_methods:
            PaymentMethod.objects.get_or_create(
                name=method["name"],
                defaults={
                    "description": method["description"],
                    "is_active": True,
                    "created_by": user
                }
            )
        types = [
            ("purchase", "quotation", "কোটেশন"),
            ("purchase", "order", "অর্ডার"),
            ("purchase", "pending", "পেন্ডিং"),
            ("purchase", "complete", "কম্প্লিট"),
            ("purchase", "cancel", "ক্যানসেল"),
            ("purchase", "deleted", "ডিলেট"),
            ("sales", "draft", "ড্রাফট"),
            ("sales", "invoice", "ইনভয়েস"),
            ("sales", "paid", "পেইড"),
            ("sales", "return", "ফেরত"),
            ("sales", "cancel", "বাতিল"),
        ]

        for module, code, name in types:
            obj, created = TransactionType.objects.get_or_create(
                code=code,
                module=module,
                defaults={"name": name}
            )
            status = "✅ Created" if created else "⚠️ Exists"
            self.stdout.write(f"{status}: {module} → {code}")
        self.stdout.write(self.style.SUCCESS("✅ ডিফল্ট ক্যাটেগরি, ব্র্যান্ড, ইউনিট, ওয়ারেন্টি যুক্ত হয়েছে"))