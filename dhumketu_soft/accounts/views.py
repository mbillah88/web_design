from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from .models import Role
from .forms import CustomUserForm, RoleForm

User = get_user_model()

def role_list(request):
    roles = Role.objects.all()
    return render(request, 'accounts/role_list.html', {'roles': roles})

def role_add(request):
    form = RoleForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    html = render_to_string('accounts/role_modal_form.html', {'form': form, 'title': 'Add Role'}, request)
    return HttpResponse(html)

def permission_matrix(request):
    roles = Role.objects.all()
    modules = Module.objects.all()
    permissions = PermissionMatrix.objects.all()
    matrix = {(p.role.id, p.module.id): p.can_access for p in permissions}
    return render(request, 'accounts/permission_matrix.html', {
        'roles': roles, 'modules': modules, 'matrix': matrix
    })

def toggle_permission(request):
    if request.method == 'POST':
        role_id = request.POST.get('role_id')
        module_id = request.POST.get('module_id')
        perm, _ = PermissionMatrix.objects.get_or_create(role_id=role_id, module_id=module_id)
        perm.can_access = not perm.can_access
        perm.save()
        return JsonResponse({'status': 'success', 'can_access': perm.can_access})
    return JsonResponse({'status': 'error'})
    
def role_edit(request, pk):
    role = get_object_or_404(Role, pk=pk)
    form = RoleForm(request.POST or None, instance=role)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    html = render_to_string('accounts/role_modal_form.html', {'form': form, 'title': 'Edit Role'}, request)
    return HttpResponse(html)

def role_delete(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        role.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

def user_list(request):
    users = User.objects.all()
    return render(request, 'accounts/user_list.html', {'users': users})

def user_add(request):
    form = CustomUserForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    html = render_to_string('accounts/user_modal_form.html', {'form': form, 'title': 'Add User'}, request)
    return HttpResponse(html)

def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = CustomUserForm(request.POST or None, instance=user)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success', 'message': 'User updated successfully!'})
        return JsonResponse({'status': 'error', 'errors': form.errors})
    html = render_to_string('accounts/user_modal_form.html', {'form': form, 'title': 'Edit User'}, request)
    return HttpResponse(html)

def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.delete()
    messages.success(request, "User deleted successfully!")
    return redirect('user_list')

def user_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, 'accounts/user_view.html', {'user': user})

def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})
    