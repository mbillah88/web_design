# accounts/context_processors.py
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
    modules = Module.objects.filter(is_visible=True).select_related('parent')

    return {
        'modules': modules,
        'role_permissions': permissions
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
