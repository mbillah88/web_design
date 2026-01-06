# accounts/views.py
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from accounts.context_processors import has_permission
from accounts.models import CustomUser, Role, Profile, Permission, Module, ModuleGroup
from accounts.forms import RoleForm, DashboardForm, UserForm, ModuleForm, ProfileForm, Department
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.urls import get_resolver
from django.conf import settings
import json



User = get_user_model()

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard_view')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')   
def logout_view(request):
    logout(request)
    return redirect('login')
@login_required
def dashboard(request):
    return render(request, 'accounts/dashboard.html')

@login_required
def user_list(request):
    if not has_permission(request, 'user_list', 'can_access'):
        return redirect('no_permission')
    users = CustomUser.objects.all()
    roles = Role.objects.all()
    return render(request, 'accounts/user_list.html', {'users': users, 'roles': roles})
@login_required
def user_form_handler(request, user_id=None):
    if user_id:
        if not has_permission(request, 'user_list', 'can_edit'):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        user = get_object_or_404(CustomUser, id=user_id)
    else:
        if not has_permission(request, 'user_list', 'can_create'):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        user = None

    form = UserForm(request.POST or None, instance=user)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True})
    return JsonResponse({'error': form.errors}, status=400)

@login_required
def user_add(request):
    if not has_permission(request, 'user_list', 'can_create'):
        return redirect('no_permission')

    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('user_list')

    # Optional: render fallback page with form errors
    return render(request, 'accounts/user_list.html', {
        'form': form,
        'users': CustomUser.objects.all(),
        'roles': Role.objects.all(),
        'form_error': True
    })

@login_required
def user_edit(request, user_id):
    if not has_permission(request, 'user_list', 'can_edit'):
        return redirect('no_permission')
    user = get_object_or_404(CustomUser, id=user_id)
    form = UserEditForm(request.POST or None, instance=user)
    if form.is_valid():
        form.save()
        return redirect('user_list')
    return render(request, 'accounts/edit_user.html', {'form': form})

@login_required
def user_delete(request, user_id):
    if request.method == 'POST':
        if not has_permission(request, 'user_list', 'can_delete'):
            return redirect('no_permission')

        user = get_object_or_404(CustomUser, id=user_id)
        
        if user.is_protected:
            messages.error(request, "❌ এই ইউজার সুরক্ষিত, ডিলেট করা যাবে না")
            return redirect('user_list')

        user.delete()
        messages.success(request, "✅ ইউজার সফলভাবে মুছে ফেলা হয়েছে")
        return redirect('user_list')
    return redirect('user_list')

def profile_form_view(request, user_id):
    profile = get_object_or_404(Profile, user__id=user_id)
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)
    departments = Department.objects.all()

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('profile_view', user_id=user_id)

    return render(request, 'accounts/profile_edit.html', {
        'form': form,
        'profile': profile,
        'departments': departments
    })

def profile_view_page(request, user_id):
    profile = get_object_or_404(Profile, user__id=user_id)
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)
    departments = Department.objects.all()

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('profile_view', user_id=user_id)

    return render(request, 'accounts/profile_view.html', {
        'profile': profile,
        'form': form,
        'departments': departments
    })

# ✅ Role List
@login_required
def role_list(request):
    access_action = ActionType.objects.filter(key='access').first()
    has_access = Permission.objects.filter(
        role=request.user.role,
        module__url_name='role_list',
        action=access_action,
        is_allowed=True
    ).exists()

    if not has_access:
        return render(request, '403.html', {
            'reason': "এই রোল তালিকা দেখার অনুমতি নেই।"
        })

    roles = Role.objects.all().order_by('name')
    return render(request, 'accounts/role_list.html', {
        'roles': roles,
        'page_title': 'রোল তালিকা'
    })


# ✅ Role Create
def role_create(request):
    form = RoleForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "✅ নতুন রোল তৈরি হয়েছে")
        return redirect('role_list')
    return render(request, 'accounts/role_form.html', {'form': form})

def create_role_view(request):
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            role = form.save()
            if role.name == 'SuperAdmin':
                assign_default_permissions(role)
            messages.success(request, "✅ রোল তৈরি হয়েছে")
            return redirect('role_list')

# ✅ Role Edit
def role_edit(request, role_id):
    role = get_object_or_404(Role, id=role_id)
    form = RoleForm(request.POST or None, instance=role)
    if form.is_valid():
        form.save()
        messages.success(request, "✅ রোল আপডেট হয়েছে")
        return redirect('role_list')
    return render(request, 'accounts/role_form.html', {'form': form, 'role': role})

# ✅ Role Delete
def role_delete(request, role_id):
    role = get_object_or_404(Role, id=role_id)

    if request.method == 'POST':
        role.delete()
        messages.success(request, f"✅ রোল '{role.name}' সফলভাবে মুছে ফেলা হয়েছে")
        return redirect('role_list')

    messages.error(request, "❌ অননুমোদিত অনুরোধ")
    return redirect('role_list')

# ✅ Role Cloning
def clone_role(request, role_id):
    original = get_object_or_404(Role, id=role_id)
    new_role = Role.objects.create(name=f"{original.name} (কপি)")
    for perm in Permission.objects.filter(role=original):
        Permission.objects.create(
            role=new_role,
            module=perm.module,
            can_access=perm.can_access,
            can_create=perm.can_create,
            can_edit=perm.can_edit,
            can_delete=perm.can_delete
        )
    messages.success(request, f"✅ '{original.name}' রোল সফলভাবে ক্লোন করা হয়েছে")
    return redirect('role_permission_edit', role_id=new_role.id)

# ✅ Granular Permission UI
def role_permission_edit(request, role_id):
    role = get_object_or_404(Role, id=role_id)
    modules = Module.objects.all()
    actions = ['access', 'create', 'edit', 'delete']
    permissions = {}

    for module in modules:
        perm = Permission.objects.filter(role=role, module=module).first()
        permissions[str(module.id)] = {
            'access': perm.can_access if perm else False,
            'create': perm.can_create if perm else False,
            'edit': perm.can_edit if perm else False,
            'delete': perm.can_delete if perm else False,
        }

    if request.method == 'POST':
        for module in modules:
            perm, _ = Permission.objects.get_or_create(role=role, module=module)
            for action in actions:
                setattr(perm, f"can_{action}", f"{module.id}_{action}" in request.POST)
            perm.save()
        messages.success(request, "✅ পারমিশন সফলভাবে সংরক্ষণ হয়েছে")
        return redirect('role_list')

    return render(request, 'accounts/role_permission_form.html', {
    'role': role,
    'modules': modules,
    'permissions': permissions,  # dict[module.id][action]
    'actions': ['access', 'create', 'edit', 'delete']
})

# ডিপার্টমেন্ট ...
def ajax_add_department(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        description = request.POST.get('description', '')

        if not name or not code:
            return JsonResponse({'success': False, 'error': 'নাম এবং কোড আবশ্যক'})

        dept = Department.objects.create(name=name, code=code, description=description)
        return JsonResponse({
            'success': True,
            'department': {
                'id': dept.id,
                'name': dept.name,
                'code': dept.code,
                'description': dept.description
            }
        })

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)
# Module Management
@csrf_exempt
def sync_modules_ajax(request):
    if request.method == 'POST' and request.user.is_authenticated:
        resolver = get_resolver()
        url_names = [name for name in resolver.reverse_dict.keys() if isinstance(name, str)]
        added = 0

        for url_name in url_names:
            if not Module.objects.filter(url_name=url_name).exists():
                Module.objects.create(
                    name=url_name.replace('_', ' ').title(),
                    url_name=url_name,
                    icon='bi-circle'
                )
                added += 1

        return JsonResponse({'success': True, 'added': added})
    return JsonResponse({'success': False, 'error': 'Invalid request'})
def module_list(request):
    with open(settings.BASE_DIR / 'static/icons.json', 'r') as f:
        icon_list = json.load(f)

    modules = Module.objects.all()
    return render(request, 'accounts/module_list.html', {
        'modules': modules,
        'all_modules': modules,
        'icon_list': icon_list
    })
@csrf_exempt
def module_form_handler(request, module_id=None):
    instance = Module.objects.filter(id=module_id).first() if module_id else None
    form = ModuleForm(request.POST or None, instance=instance)

    if request.method == 'POST':
        if form.is_valid():
            module = form.save()
            return JsonResponse({
                'success': True,
                'created': module_id is None,
                'module': {
                    'id': module.id,
                    'name': module.name
                }
            })
        return JsonResponse({
            'success': False,
            'error': form.errors.get_json_data()
        })

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)
def module_delete(request, module_id):
    if request.method == 'POST':
        module = get_object_or_404(Module, id=module_id)
        module.delete()
    return redirect('module_list')
def module_list_view(request):
    with open(settings.BASE_DIR / 'static/icons.json', 'r') as f:
        icon_list = json.load(f)
        
    modules = Module.objects.select_related('group', 'parent').all()
    module_groups = ModuleGroup.objects.all().order_by('order')
    parent_modules = Module.objects.filter(parent__isnull=True, is_visible=True).order_by('order')
    
    return render(request, 'accounts/module_list.html', {
        'modules': modules,
        'module_groups': module_groups,  # ✅ এই context পাঠাও
        'parent_modules': parent_modules,
        'all_modules': modules,
        'icon_list': icon_list
       
    })

def module_group_list_view(request):
    groups = ModuleGroup.objects.all().order_by('order')
    return render(request, 'accounts/module_group_list.html', {
        'module_groups': groups
    })    
@csrf_exempt
def module_group_save_ajax(request):
    if request.method == "POST":
        group_id = request.POST.get("id")
        name = request.POST.get("name", "").strip()
        icon = request.POST.get("icon", "").strip()
        order = int(request.POST.get("order", 0))

        if not name:
            return JsonResponse({"success": False, "error": "গ্রুপ নাম আবশ্যক"})

        if group_id:
            group = ModuleGroup.objects.filter(id=group_id).first()
            if not group:
                return JsonResponse({"success": False, "error": "গ্রুপ পাওয়া যায়নি"})
            group.name = name
            group.icon = icon
            group.order = order
            group.save()
            return JsonResponse({"success": True, "created": False, "group": {
                "id": group.id, "name": group.name, "icon": group.icon, "order": group.order
            }})
        else:
            group = ModuleGroup.objects.create(name=name, icon=icon, order=order)
            return JsonResponse({"success": True, "created": True, "group": {
                "id": group.id, "name": group.name, "icon": group.icon, "order": group.order
            }})

    return JsonResponse({"success": False, "error": "Invalid request"})
def module_group_delete(request, id):
    if request.method == "POST":
        ModuleGroup.objects.filter(id=id).delete()
        return redirect('module_group_list')
