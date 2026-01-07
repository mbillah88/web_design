# accounts/context_processors.py
from accounts.models import Permission, ModuleGroup, Module, ActionType
from django.urls import reverse, NoReverseMatch
from accounts.constants import MODULE_LAYOUT

# Optional: Custom label mapping (for Bangla or display override)
LABEL_MAP = {
    "accounts:dashboard": "Dashboard",
    "accounts:user_list": "ইউজার তালিকা",
    "accounts:role_list": "রোল ম্যানেজমেন্ট",
    "products:product_list": "পণ্য তালিকা"
}
def sidebar_modules(request):
    if not request.user.is_authenticated:
        return {}

    role = getattr(request.user, 'role', None)
    if not role:
        return {}

    access_perms = Permission.objects.filter(role=role, is_allowed=True, action__key='access')
    allowed_modules = Module.objects.filter(id__in=access_perms.values('module_id'), is_visible=True)

    grouped = {}
    for module in allowed_modules.select_related('group'):
        group_name = module.group.name if module.group else 'Other'
        grouped.setdefault(group_name, []).append(module)

    return {'sidebar_modules': grouped}

def header_modules(request):
    if not request.user.is_authenticated:
        return {}

    role = getattr(request.user, 'role', None)
    if not role:
        return {}

    access_perms = Permission.objects.filter(role=role, is_allowed=True, action__key='access')
    header_modules = Module.objects.filter(id__in=access_perms.values('module_id'), is_header=True)

    return {'header_modules': header_modules}
def sidebar_context(request):
    role = getattr(request.user, 'role', None)
    access_action = ActionType.objects.filter(key='access').first()

    perms = Permission.objects.filter(role=role, action=access_action, is_allowed=True)
    allowed_modules = [p.module for p in perms if p.module.is_visible]

    current_view = request.resolver_match.view_name if request.resolver_match else None
    sidebar_groups = {}

    for mod in sorted(allowed_modules, key=lambda m: m.order):
        if mod.parent:
            continue  # ✅ Skip child modules

        group_name = mod.group.name if mod.group else "General"
        group_icon = mod.group.icon if mod.group else "bi-folder"

        if group_name not in sidebar_groups:
            sidebar_groups[group_name] = {
                "name": group_name,
                "icon": group_icon,
                "modules": [],
                "active": False
            }

        try:
            url = reverse(mod.url_name)
        except NoReverseMatch:
            url = "#"

        label = mod.label or mod.name or mod.url_name.split(":")[-1].replace("_", " ").title()

        module_data = {
            "name": label,
            "url_name": mod.url_name,
            "icon": mod.icon,
            "url": url,
            "is_active": mod.url_name == current_view
        }

        sidebar_groups[group_name]["modules"].append(module_data)

        if module_data["is_active"]:
            sidebar_groups[group_name]["active"] = True

    return {
        "sidebar_groups": list(sidebar_groups.values()),
        "user_role": role.name if role else "Guest"
    }
def sidebar_context১(request):
    role = getattr(request.user, 'role', None)
    access_action = ActionType.objects.filter(key='access').first()

    # ✅ Filter allowed + visible modules
    perms = Permission.objects.filter(role=role, action=access_action, is_allowed=True)
    allowed_modules = [p.module for p in perms if p.module.is_visible]

    current_view = request.resolver_match.view_name if request.resolver_match else None
    sidebar_groups = {}

    for mod in sorted(allowed_modules, key=lambda m: m.order):
        # ✅ Skip child modules (used in modals/forms)
        if mod.parent:
            continue

        # ✅ Determine group name and icon
        group_name = mod.group.name if mod.group else "General"
        group_icon = mod.group.icon if mod.group else "bi-folder"

        if group_name not in sidebar_groups:
            sidebar_groups[group_name] = {
                "name": group_name,
                "icon": group_icon,
                "modules": [],
                "active": False
            }

        # ✅ Safe reverse
        try:
            url = reverse(mod.url_name)
        except NoReverseMatch:
            url = "#"

        # ✅ Label fallback
        label = getattr(mod, 'label', None) or mod.name or mod.url_name.split(":")[-1].replace("_", " ").title()

        module_data = {
            "name": label,
            "url_name": mod.url_name,
            "icon": mod.icon,
            "url": url,
            "is_active": mod.url_name == current_view
        }

        sidebar_groups[group_name]["modules"].append(module_data)

        if module_data["is_active"]:
            sidebar_groups[group_name]["active"] = True

    return {
        "sidebar_groups": list(sidebar_groups.values()),
        "user_role": role.name if role else "Guest"
    }
def sidebar_context১(request):
    role = getattr(request.user, 'role', None)
    access_action = ActionType.objects.filter(key='access').first()

    # ✅ Filter allowed modules
    perms = Permission.objects.filter(role=role, action=access_action, is_allowed=True)
    allowed_modules = [p.module for p in perms if p.module.is_visible]

    current_view = request.resolver_match.view_name if request.resolver_match else None
    sidebar_groups = {}

    for mod in sorted(allowed_modules, key=lambda m: m.order):
        # ✅ Skip child modules (they're not shown in sidebar)
        if mod.parent:
            continue

        # ✅ Determine group name (fallback if None)
        group_name = mod.group.name if mod.group else "General"

        if group_name not in sidebar_groups:
            sidebar_groups[group_name] = {
                "name": group_name,
                "icon": mod.group.icon if mod.group else "bi-folder",
                "modules": [],
                "active": False
            }

        # ✅ Safe URL reverse
        try:
            url = reverse(mod.url_name)
        except NoReverseMatch:
            url = "#"

        label = mod.label or mod.name or mod.url_name.split(":")[-1].replace("_", " ").title()

        module_data = {
            "name": label,
            "url_name": mod.url_name,
            "icon": mod.icon,
            "url": url,
            "is_active": mod.url_name == current_view
        }

        sidebar_groups[group_name]["modules"].append(module_data)

        if module_data["is_active"]:
            sidebar_groups[group_name]["active"] = True

    # ✅ Convert dict to list for template
    return {
        "sidebar_groups": list(sidebar_groups.values()),
        "user_role": role.name if role else "Guest"
    }
def has_permission(request, module_url_name, action_key):
    user = request.user
    role = getattr(user, 'role', None)
    if not role:
        return False
    try:
        module = Module.objects.get(url_name=module_url_name)
        action = ActionType.objects.get(key=action_key)
        perm = Permission.objects.get(role=role, module=module, action=action)
        return perm.is_allowed
    except:
        return False