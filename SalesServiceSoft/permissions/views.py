from django.shortcuts import render
from django.http import JsonResponse
from .models import Role, Module, RoleModulePermission

def permission_matrix(request):
    roles = Role.objects.all()
    modules = Module.objects.all()
    permissions = RoleModulePermission.objects.all()
    matrix = {
        (perm.role.id, perm.module.id): perm.can_access
        for perm in permissions
    }
    return render(request, 'permissions/matrix.html', {
        'roles': roles,
        'modules': modules,
        'matrix': matrix
    })

def toggle_permission(request):
    if request.method == 'POST':
        role_id = request.POST.get('role_id')
        module_id = request.POST.get('module_id')
        try:
            perm, created = RoleModulePermission.objects.get_or_create(
                role_id=role_id, module_id=module_id
            )
            perm.can_access = not perm.can_access
            perm.save()
            return JsonResponse({'status': 'success', 'can_access': perm.can_access})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
