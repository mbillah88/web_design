# accounts/templatetags/custom_tags.py

from django import template
from accounts.models import Module, Permission, ActionType

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def dict_get(d, key):
    return d.get(key, False)

@register.filter 
def dict_gets(d, key): 
    return d.get(key, "—")

@register.simple_tag
def nested_get(permissions, module_id, action):
    return permissions.get(str(module_id), {}).get(action, False)
    
@register.simple_tag(takes_context=True)
def can_access(context, module_url_name):
    return _check_permission(context, module_url_name, 'access')

@register.simple_tag(takes_context=True)
def can_create(context, module_url_name):
    return _check_permission(context, module_url_name, 'create')

@register.simple_tag(takes_context=True)
def can_edit(context, module_url_name):
    return _check_permission(context, module_url_name, 'edit')

@register.simple_tag(takes_context=True)
def can_delete(context, module_url_name):
    return _check_permission(context, module_url_name, 'delete')

def _check_permission(context, module_url_name, action_key):
    request = context.get('request')
    user = getattr(request, 'user', None)
    role = getattr(user, 'role', None)
    if not role:
        return False

    try:
        module = Module.objects.get(url_name=module_url_name)
        action = ActionType.objects.get(key=action_key)
        perm = Permission.objects.get(role=role, module=module, action=action)
        return perm.is_allowed
    except (Module.DoesNotExist, ActionType.DoesNotExist, Permission.DoesNotExist):
        return False

def has_permission(request, url_name, action_key='access'):
    role = getattr(request.user, 'role', None)
    action = ActionType.objects.filter(key=action_key).first()
    if not role or not action:
        return False
    return Permission.objects.filter(
        role=role,
        module__url_name=url_name,
        action=action,
        is_allowed=True
    ).exists()

@register.simple_tag
def flat_permission_check(matrix, module_url, action_key):
    return matrix.get((module_url, action_key), False)

@register.filter
def get_matrix_value(matrix, args):
    role_id, module_id, action_key = args.split(',')
    return matrix.get(int(role_id), {}).get(int(module_id), {}).get(action_key, False)

@register.filter
def json_safe(value):
    return 
