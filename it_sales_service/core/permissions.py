from accounts.models import Permission

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

