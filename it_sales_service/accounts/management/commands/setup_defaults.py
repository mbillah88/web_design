from django.core.management.base import BaseCommand
from django.db import connections, OperationalError
from django.contrib.auth.hashers import make_password
from django.urls import get_resolver
from accounts.models import Role, ModuleGroup, Module, Permission, CustomUser, Department, Profile
from core.constants import MODULE_LAYOUT #MODULE_STRUCTURE

class Command(BaseCommand):
    help = "🛠️ ফুল সিস্টেম সেটআপ: রোল, ইউজার, প্রোফাইল, মডিউল, গ্রুপ, পারমিশন"

    def handle(self, *args, **kwargs):
        # 1️⃣ DB Check
        try:
            connections['default'].ensure_connection()
            self.stdout.write(self.style.SUCCESS("✅ ডাটাবেজ সংযোগ সফল"))
        except OperationalError:
            self.stdout.write(self.style.ERROR("❌ ডাটাবেজ সংযোগ ব্যর্থ"))
            return

        # 2️⃣ Migrate
        from django.core.management import call_command
        call_command('migrate', interactive=False)
        self.stdout.write(self.style.SUCCESS("✅ মাইগ্রেশন সম্পন্ন"))

        # 3️⃣ Role
        role, _ = Role.objects.get_or_create(name="SystemAdmin", defaults={"is_protected": True})

        # 4️⃣ Department
        dept, _ = Department.objects.get_or_create(name="Administration", code="ADM")

        # 5️⃣ Admin User
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

        # 6️⃣ Profile
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.department = dept
        profile.designation = "System Administrator"
        profile.save()

        # ✅ Save all ModuleGroups and Modules
        for group_name, modules in MODULE_LAYOUT.items():
            group, _ = ModuleGroup.objects.get_or_create(name=group_name)

            for parent_url, config in modules.items():
                if config is None:
                    # Direct module (e.g. dashboard)
                    Module.objects.get_or_create(
                        url_name=parent_url,
                        defaults={
                            "name": parent_url.replace('_', ' ').title(),
                            "group": group,
                            "icon": "bi-speedometer",
                            "is_visible": True,
                            "order": 0
                        }
                    )
                else:
                    # Parent module
                    parent, _ = Module.objects.get_or_create(
                        url_name=parent_url,
                        defaults={
                            "name": parent_url.replace('_', ' ').title(),
                            "group": group,
                            "icon": config.get("icon", "bi-folder"),
                            "is_visible": True,
                            "order": 0
                        }
                    )
                    # Child actions
                    for child_url in config.get("children", []):
                        Module.objects.get_or_create(
                            url_name=child_url,
                            defaults={
                                "name": child_url.replace('_', ' ').title(),
                                "group": group,
                                "parent": parent,
                                "icon": "bi-circle",
                                "is_visible": True,
                                "order": 0
                            }
                        )

        # ✅ Assign access only to Accounts modules
        accounts_group = ModuleGroup.objects.filter(name__icontains="Accounts").first()
        accounts_modules = Module.objects.filter(group=accounts_group)

        for module in Module.objects.all():
            perm, _ = Permission.objects.get_or_create(role=role, module=module)
            if module in accounts_modules:
                perm.can_access = True
                perm.can_create = True
                perm.can_edit = True
                perm.can_delete = True
            else:
                perm.can_access = False
                perm.can_create = False
                perm.can_edit = False
                perm.can_delete = False
            perm.save()

        self.stdout.write(self.style.SUCCESS("✅ All modules saved. SystemAdmin has access only to Accounts."))
        self.stdout.write(self.style.SUCCESS("🎉 ফুল সিস্টেম সেটআপ সম্পন্ন ✅"))
