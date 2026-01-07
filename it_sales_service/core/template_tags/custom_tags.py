# accounts/templatetags/custom_tags.py

from django import template
from accounts.models import Module, Permission

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.simple_tag
def nested_get(permissions, module_id, action):
    return permissions.get(str(module_id), {}).get(action, False)
        
@register.filter(name='can_access')
def can_access(request, module_url_name):
    user = request.user
    role = getattr(user, 'role', None)
    if not role:
        return False
    try:
        module = Module.objects.get(url_name=module_url_name)
        perm = Permission.objects.get(role=role, module=module)
        return perm.can_access
    except:
        return False

@register.simple_tag(takes_context=True)
def can_create(context, module_url_name):
    return _check_permission(context, module_url_name, 'can_create')

@register.simple_tag(takes_context=True)
def can_edit(context, module_url_name):
    return _check_permission(context, module_url_name, 'can_edit')

@register.simple_tag(takes_context=True)
def can_delete(context, module_url_name):
    return _check_permission(context, module_url_name, 'can_delete')

def _check_permission(context, module_url_name, action):
    request = context.get('request')
    user = request.user
    role = getattr(user, 'role', None)
    if not role:
        return False
    try:
        module = Module.objects.get(url_name=module_url_name)
        perm = Permission.objects.get(role=role, module=module)
        return getattr(perm, action, False)
    except:
        return False

@register.simple_tag
def has_permission(permissions, url_name, action):
    return permissions.get(url_name, {}).get(action, False)
