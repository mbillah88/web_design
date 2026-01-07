from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from accounts.models import Role, Module, Permission, CustomUser, Department, Profile

class Command(BaseCommand):
    help = "🔐 Setup default SystemAdmin role, admin user, department, profile, and permissions"

    def handle(self, *args, **kwargs):
        # 1️⃣ Create Role
        role, role_created = Role.objects.get_or_create(name="SystemAdmin")
        if role_created:
            self.stdout.write(self.style.SUCCESS("✅ Role 'SystemAdmin' created"))
        else:
            self.stdout.write("ℹ️ Role 'SystemAdmin' already exists")

        # 2️⃣ Create Department
        dept, dept_created = Department.objects.get_or_create(name="Administration", code="ADM")
        if dept_created:
            self.stdout.write(self.style.SUCCESS("✅ Department 'Administration' created"))
        else:
            self.stdout.write("ℹ️ Department 'Administration' already exists")

        # 3️⃣ Create Admin User
        user, user_created = CustomUser.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "is_staff": True,
                "is_superuser": True,
                "role": role,
                "password": make_password("admin123")
            }
        )
        if user_created:
            self.stdout.write(self.style.SUCCESS("✅ Admin user created"))
        else:
            self.stdout.write("⚠️ Admin user already exists")

        # 4️⃣ Create Profile
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.department = dept
        profile.designation = "System Administrator"
        profile.save()
        self.stdout.write("✅ Profile updated")

        # 5️⃣ Assign Full Permissions to All Modules
        modules = Module.objects.all()
        actions = ['can_access', 'can_create', 'can_edit', 'can_delete']
        added = 0

        for module in modules:
            perm, created = Permission.objects.get_or_create(role=role, module=module)
            for action in actions:
                setattr(perm, action, True)
            perm.save()
            if created:
                added += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Permissions assigned for {modules.count()} modules ({added} new)"))
        self.stdout.write(self.style.SUCCESS("🎉 Default SystemAdmin setup completed"))
