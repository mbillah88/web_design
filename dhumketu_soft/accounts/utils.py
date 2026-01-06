# accounts/utils.py
from permissions.models import Module, RoleModulePermission

def get_allowed_modules(user):
    if not user.is_authenticated or not user.role:
        return []
    return Module.objects.filter(
        rolemodulepermission__role=user.role,
        rolemodulepermission__can_access=True
    )
