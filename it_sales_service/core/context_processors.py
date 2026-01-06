from accounts.models import ModuleGroup
from core.permissions import get_role_permissions
from core.constants import URL_ARG_MAPPING
from accounts.models import Role, CustomUser, Permission, Module

def sidebar_modules(request):
    if not request.user.is_authenticated:
        return {}

    role = getattr(request.user, 'role', None)
    if not role:
        return {}

    permissions = Permission.objects.filter(role=role, can_access=True).select_related('module')
    modules = [p.module for p in permissions]

    sidebar = {}
    for module in modules:
        if module.parent:
            sidebar.setdefault(module.parent.id, []).append(module)
        else:
            sidebar.setdefault(module.id, [])

    parent_modules = Module.objects.filter(id__in=sidebar.keys()).order_by('order')

    return {
        'parents': parent_modules,
        'children': sidebar
    }

def sidebar_context(request):
    role = getattr(request.user, 'role', None)
    permissions = get_role_permissions(role) if role else {}
    active_id = request.user.id if request.user.is_authenticated else None

    module_groups = ModuleGroup.objects.order_by('order')
    sidebar_structure = []

    current_url = request.resolver_match.url_name if request.resolver_match else None

    for group in module_groups:
        parent_modules = Module.objects.filter(group=group, parent__isnull=True, is_visible=True).order_by('order')
        filtered_parents = [m for m in parent_modules if permissions.get(m.url_name, {}).get('access')]

        group_data = {
            'name': group.name,
            'icon': group.icon,
            'modules': [],
            'active': False  # ✅ default
        }

        for m in filtered_parents:
            is_active = m.url_name == current_url
            group_data['modules'].append({
                'name': m.name,
                'url_name': m.url_name,
                'icon': m.icon,
                'is_active': is_active
            })

            if is_active:
                group_data['active'] = True  # ✅ mark group as active

        sidebar_structure.append(group_data)
        
    return {
        'sidebar_groups': sidebar_structure,
        'role_permissions': permissions,
        'user_role': role.name if role else "অনির্ধারিত"
    }

def breadcrumb_context(request):
    try:
        current_url_name = request.resolver_match.url_name
        current_module = Module.objects.filter(url_name=current_url_name).select_related('parent').first()
        breadcrumb = []
        if current_module:
            if current_module.parent:
                breadcrumb.append({'name': current_module.parent.name})
            breadcrumb.append({'name': current_module.name})
        else:
            breadcrumb.append({'name': 'Dashboard'})
        return {'breadcrumb_items': breadcrumb}
    except:
        return {'breadcrumb_items': [{'name': 'Dashboard'}]}

def has_permission(request, module_name, action='can_access'):
    if not request.user.is_authenticated or not request.user.role:
        return False
    try:
        module = Module.objects.get(url_name=module_name)
        perm = Permission.objects.get(role=request.user.role, module=module)
        return getattr(perm, action, False)
    except:
        return False

def get_role_permissions(role):
    permissions = Permission.objects.filter(role=role)
    perm_dict = {}
    for perm in permissions:
        perm_dict[perm.module.url_name] = {
            'access': perm.can_access,
            'create': perm.can_create,
            'edit': perm.can_edit,
            'delete': perm.can_delete
        }
    return perm_dict

def user_profile_context(request):
    if request.user.is_authenticated:
        try:
            return {'user_profile_image': request.user.profile.profile_image.url}
        except:
            return {'user_profile_image': None}
    return {}
