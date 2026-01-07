from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import *
from accounts.forms import *
from accounts.constants import MODULE_LAYOUT
from accounts.context_processors import has_permission
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.urls import get_resolver
from django.conf import settings
import json
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from django.utils.timezone import now
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_protect


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')   
def logout_view(request):
    logout(request)
    return redirect('accounts:login')   

@login_required
def dashboard(request):
    current_url = request.resolver_match.view_name if request.resolver_match else None
    access_action = ActionType.objects.filter(key='access').first()

    print(f"Current URL: {current_url}, Access Action: {access_action}")

    if not access_action or not current_url:
        return render(request, 'accounts/403.html', {
            'reason': "❌ অনুমতি যাচাই করতে ব্যর্থ হয়েছে"
        })

    has_access = Permission.objects.filter(
        role=request.user.role,
        module__url_name=current_url,  # ✅ Now matches "accounts:dashboard"
        action=access_action,
        is_allowed=True
    ).exists()

    if not has_access:
        return render(request, 'accounts/403.html', {
            'reason': f"❌ আপনি '{current_url}' পেজে প্রবেশের অনুমতি রাখেন না"
        })
    # Debugging output    
    print(f"🔍 Checking permission for: {current_url}")

    return render(request, 'accounts/dashboard.html', {
        'page_title': 'ড্যাশবোর্ড',
        'welcome_text': f"স্বাগতম, {request.user.get_full_name()}!",
        'role': request.user.role,
        'user': request.user,
    })

@login_required
def role_list(request):
    # ✅ Namespace-aware permission check
    if not has_permission(request, 'accounts:role_list', 'access'):
        return render(request, 'accounts/403.html', {
            'reason': "❌ আপনি Role Management পৃষ্ঠায় প্রবেশের অনুমতি রাখেন না"
        })

    roles = Role.objects.all()
    for role in roles:
        role.is_protected = bool(role.is_protected)  # ✅ Ensure boolean for UI toggle

    modules = Module.objects.filter(is_visible=True, parent=None).order_by('order')
    actions = ActionType.objects.all()

    return render(request, 'accounts/role_list.html', {
        'page_title': 'Role Management',
        'user': request.user,
        'role': request.user.role,
        'roles': roles,
        'modules': modules,
        'actions': actions
    })
@login_required
@csrf_exempt
def role_form_handler(request, role_id=None):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

    if role_id:
        if not has_permission(request, 'accounts:role_edit', 'edit'):
            return JsonResponse({'success': False, 'error': {'permission': ['আপনার সম্পাদনার অনুমতি নেই']}}, status=403)
        role = get_object_or_404(Role, id=role_id)
    else:
        if not has_permission(request, 'accounts:role_create', 'create'):
            return JsonResponse({'success': False, 'error': {'permission': ['আপনার যোগ করার অনুমতি নেই']}}, status=403)
        role = Role()

    role.name = request.POST.get('name', '').strip()
    if not role.name:
        return JsonResponse({'success': False, 'error': {'name': ['রোলের নাম আবশ্যক']}}, status=400)

    try:
        role.save()
        return JsonResponse({'success': True})
    except IntegrityError:
        return JsonResponse({'success': False, 'error': {'name': ['এই নাম ইতিমধ্যে আছে']}}, status=400)

@require_POST
@login_required
def role_form(request, role_id=None):
    name = request.POST.get('name')
    is_protected = request.POST.get('is_protected') == 'on'

    if not name:
        return JsonResponse({'success': False, 'error': {'name': ['রোল নাম আবশ্যক']}})

    if role_id:
        role = get_object_or_404(Role, id=role_id)
        role.name = name
        role.is_protected = is_protected
        role.save()
        return JsonResponse({'success': True})
    else:
        role = Role(name=name, is_protected=is_protected)
        role.save()
        return JsonResponse({'success': True, 'role_id': role.id})
@require_POST
@login_required
def role_delete(request, role_id):
    role = get_object_or_404(Role, id=role_id)
    if role.is_protected:
        return render(request, 'accounts/403.html', {'reason': '🔒 সুরক্ষিত রোল মুছে ফেলা যাবে না'})
    role.delete()
    return redirect('accounts:role_list')
@login_required
def role_clone_view(request, source_role_id):
    source = get_object_or_404(Role, id=source_role_id)
    clone = Role.objects.create(
        name=f"{source.name} (Clone)",
        is_protected=False
    )
    Permission.objects.bulk_create([
        Permission(role=clone, module=p.module, action=p.action, is_allowed=p.is_allowed)
        for p in Permission.objects.filter(role=source)
    ])
    return redirect('accounts:role_list')
@login_required
def permission_matrix_view(request):
    roles = Role.objects.all()
    role_id = request.GET.get('role_id')
    selected_role = get_object_or_404(Role, id=role_id) if role_id else roles.first()

    modules = Module.objects.select_related('group').all()
    actions = ActionType.objects.all()

    grouped_modules = {}
    for module in modules:
        group_name = module.group.name if module.group else 'Other'
        grouped_modules.setdefault(group_name, []).append(module)

        module.permission_map = {}
        module.allowed_count = 0
        module.denied_count = 0

        for action in actions:
            perm = Permission.objects.filter(role=selected_role, module=module, action=action).first()
            is_allowed = perm.is_allowed if perm else False
            module.permission_map[action.id] = is_allowed

            if is_allowed:
                module.allowed_count += 1
            else:
                module.denied_count += 1

    return render(request, 'accounts/permission_matrix.html', {
        'roles': roles,
        'selected_role': selected_role,
        'grouped_modules': grouped_modules,
        'actions': actions,
    })
@require_POST
@login_required
def permission_matrix_save(request, role_id):
    role = get_object_or_404(Role, id=role_id)
    Permission.objects.filter(role=role).delete()

    perms = request.POST.getlist('permissions')
    for item in perms:
        module_id, action_id = map(int, item.split('_'))
        module = Module.objects.get(id=module_id)
        action = ActionType.objects.get(id=action_id)
        Permission.objects.create(role=role, module=module, action=action, is_allowed=True)

    messages.success(request, 'পারমিশন সফলভাবে সংরক্ষণ হয়েছে')
    return redirect('role_list')
@require_POST
@login_required
def update_permission(request):
    data = json.loads(request.body)

    role = get_object_or_404(Role, id=data['role_id'])
    module = get_object_or_404(Module, id=data['module_id'])
    action = get_object_or_404(ActionType, id=data['action_id'])

    if role.is_protected:
        return JsonResponse({'success': False, 'error': '🚫 এই রোল পরিবর্তনযোগ্য নয়'})

    perm, created = Permission.objects.get_or_create(
        role=role,
        module=module,
        action=action,
        defaults={'is_allowed': data['is_allowed']}
    )
    if not created:
        perm.is_allowed = data['is_allowed']
        perm.save()

    return JsonResponse({'success': True})
@require_POST
def grant_all_permissions_view(request):
    data = json.loads(request.body)
    role = get_object_or_404(Role, id=data['role_id'])

    if role.is_protected:
        return JsonResponse({'success': False, 'error': '🚫 এই রোল পরিবর্তনযোগ্য নয়'})

    for module in Module.objects.all():
        for action in ActionType.objects.all():
            perm, created = Permission.objects.get_or_create(
                role=role, module=module, action=action,
                defaults={'is_allowed': True}
            )
            if not created:
                perm.is_allowed = True
                perm.save()

    return JsonResponse({'success': True})
@require_POST
def revoke_all_permissions_view(request):
    data = json.loads(request.body)
    role = get_object_or_404(Role, id=data['role_id'])

    if role.is_protected:
        return JsonResponse({'success': False, 'error': '🚫 এই রোল পরিবর্তনযোগ্য নয়'})

    Permission.objects.filter(role=role).update(is_allowed=False)
    return JsonResponse({'success': True})


# 🔍 ইউজার তালিকা
@login_required
def user_list(request):
    current_url = request.resolver_match.view_name if request.resolver_match else None
    access_action = ActionType.objects.filter(key='access').first()

    # ✅ Permission check with graceful fallback
    if not access_action or not current_url or not has_permission(request, current_url, 'access'):
        return render(request, 'accounts/403.html', {
            'reason': f"❌ আপনি '{current_url}' পৃষ্ঠায় প্রবেশের অনুমতি রাখেন না"
        })

    current_user = request.user
    role = current_user.role

    # ✅ Role filtering logic
    if role.name == 'SystemAdmin':
        roles = Role.objects.all()
    else:
        roles = Role.objects.exclude(name__in=['SystemAdmin', 'SuperAdmin'])

    users = CustomUser.objects.all()

    return render(request, 'accounts/user_list.html', {
        'page_title': 'User Management',
        'welcome_text': f"স্বাগতম, {current_user.get_full_name()}!",
        'user': current_user,
        'role': role,
        'users': users,
        'roles': roles
    })
@login_required
@csrf_exempt
def user_form_handler(request, user_id=None):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

    data = request.POST
    errors = {}

    if user_id:
        if not has_permission(request, 'accounts:user_list', 'edit'):
            return JsonResponse({'success': False, 'error': {'permission': ['সম্পাদনার অনুমতি নেই']}}, status=403)
        user = get_object_or_404(CustomUser, id=user_id)
    else:
        if not has_permission(request, 'accounts:user_list', 'create'):
            return JsonResponse({'success': False, 'error': {'permission': ['যোগ করার অনুমতি নেই']}}, status=403)
        user = CustomUser()
        user.date_joined = now()
        user.last_login = now()

    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    role_id = data.get('role')
    password = data.get('password')
    confirm = data.get('confirm_password')

    if not username:
        errors['username'] = ['ইউজারনেম আবশ্যক']
    elif CustomUser.objects.filter(username=username).exclude(id=user_id).exists():
        errors['username'] = ['এই ইউজারনেম ইতিমধ্যে আছে']

    if not email:
        errors['email'] = ['ইমেইল আবশ্যক']
    elif CustomUser.objects.filter(email=email).exclude(id=user_id).exists():
        errors['email'] = ['এই ইমেইল ইতিমধ্যে আছে']

    if not user_id:
        if not password:
            errors['password'] = ['পাসওয়ার্ড আবশ্যক']
        elif password != confirm:
            errors['password'] = ['পাসওয়ার্ড মিলছে না']

    if errors:
        return JsonResponse({'success': False, 'error': errors}, status=400)

    user.username = username
    user.email = email
    user.role = Role.objects.filter(id=role_id).first()
    user.is_active = bool(data.get('is_active'))
    user.is_staff = bool(data.get('is_staff'))
    user.is_superuser = bool(data.get('is_superuser'))
    user.is_protected = bool(data.get('is_protected'))

    if not user_id and password:
        user.password = make_password(password)

    try:
        user.save()
        return JsonResponse({'success': True}, status=200)
    except IntegrityError:
        return JsonResponse({'success': False, 'error': {'username': ['এই ইউজারনেম ইতিমধ্যে আছে']}}, status=400)
@require_POST
@login_required
def user_password_update(request, user_id):
    if not has_permission(request, 'user_list', 'edit'):
        return JsonResponse({'success': False, 'error': {'permission': ['পাসওয়ার্ড পরিবর্তনের অনুমতি নেই']}}, status=403)

    new_password = request.POST.get('new_password', '').strip()
    confirm = request.POST.get('confirm_password', '').strip()


    if not new_password:
        return JsonResponse({'success': False, 'error': {'new_password': ['পাসওয়ার্ড আবশ্যক']}}, status=400)
    if new_password != confirm:
        return JsonResponse({'success': False, 'error': {'new_password': ['পাসওয়ার্ড মিলছে না']}}, status=400)

    user = get_object_or_404(CustomUser, id=user_id)

    try:
        validate_password(new_password, user=user)
    except ValidationError as e:
        return JsonResponse({'success': False, 'error': {'new_password': list(e.messages)}}, status=400)

    user.set_password(new_password)
    user.save()

    AuditLog.objects.create(
        user=request.user,
        action='password_change',
        target_user=user,
        message=f"{request.user.username} changed password for {user.username}"
    )

    if request.headers.get('x-requested-with') != 'XMLHttpRequest':
        messages.success(request, "পাসওয়ার্ড সফলভাবে পরিবর্তন হয়েছে")
        return redirect('accounts:profile_view', user_id=user.id)

    return JsonResponse({'success': True})

@login_required
def password_modal_view(request):
    return render(request, 'accounts/modals/password_update.html')


# 🗑️ ইউজার ডিলিট
@login_required
def user_delete(request, user_id):
    if request.method == 'POST':
        if not has_permission(request, 'accounts:user_list', 'delete'):
            return redirect('no_permission')

        user = get_object_or_404(CustomUser, id=user_id)
        if user.is_protected:
            messages.error(request, "❌ এই ইউজার সুরক্ষিত, ডিলেট করা যাবে না")
        else:
            user.delete()
            messages.success(request, "✅ ইউজার সফলভাবে মুছে ফেলা হয়েছে")
        return redirect('accounts:user_list')
    return redirect('accounts:user_list')
# 👤 প্রোফাইল দেখুন
@login_required
def profile_view(request, user_id):
    target_user = get_object_or_404(CustomUser, pk=user_id)

    # ✅ হেডার ইউজার নিজের বা অন্যদের প্রোফাইল দেখতে পারবে
    return render(request, 'accounts/profile_view.html', {
        'target_user': target_user,
        'can_edit': request.user.is_superuser or request.user.id == target_user.id
    })
@login_required
def profile_view_page(request, user_id):
    profile = get_object_or_404(Profile, user__id=user_id)
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)
    departments = Department.objects.all()

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('accounts:profile_view', user_id=user_id)

    return render(request, 'accounts/profile_view.html', {
        'profile': profile,
        'form': form,
        'departments': departments
    })
@login_required
def profile_view_or_edit(request, user_id):
    target_user = get_object_or_404(CustomUser, pk=user_id)
    profile, created = Profile.objects.get_or_create(user=target_user)
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)
    departments = Department.objects.all()

    can_edit = request.user.is_superuser or request.user.id == target_user.id

    if request.method == 'POST':
        if not can_edit:
            return render(request, 'accounts/profile_view.html', {
                'profile': profile,
                'form': form,
                'departments': departments,
                'target_user': target_user,
                'error': "আপনার এই প্রোফাইল আপডেট করার অনুমতি নেই"
            })

        if form.is_valid():
            form.save()
            return redirect('accounts:profile_view', user_id=user_id)

    return render(request, 'accounts/profile_view.html', {
        'profile': profile,
        'form': form,
        'departments': departments,
        'target_user': target_user,
        'can_edit': can_edit
    })
@csrf_exempt
@login_required
def add_department(request):
    name = request.POST.get('name', '').strip()
    code = request.POST.get('code', '').strip()
    description = request.POST.get('description', '').strip()

    # ✅ Required validation
    if not name and not code:
        return JsonResponse({'success': False, 'error': 'নাম ও কোড আবশ্যক'}, status=400)
    elif not name:
        return JsonResponse({'success': False, 'error': 'বিভাগের নাম আবশ্যক'}, status=400)
    elif not code:
        return JsonResponse({'success': False, 'error': 'বিভাগের কোড আবশ্যক'}, status=400)

    # ✅ Optional: Pre-check for duplicates (recommended)
    if Department.objects.filter(name=name).exists():
        return JsonResponse({'success': False, 'error': f"নাম '{name}' ইতিমধ্যে ব্যবহৃত হয়েছে"}, status=400)
    if Department.objects.filter(code=code).exists():
        return JsonResponse({'success': False, 'error': f"কোড '{code}' ইতিমধ্যে ব্যবহৃত হয়েছে"}, status=400)

    # ✅ Try–except to catch DB-level error
    try:
        dept = Department.objects.create(name=name, code=code, description=description)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f"❌ ডাটাবেস সমস্যা: {str(e)}"}, status=500)

    return JsonResponse({
        'success': True,
        'message': f"✅ বিভাগ '{dept.name}' যোগ হয়েছে",
        'department': {
            'id': dept.id,
            'name': dept.name,
            'code': dept.code,
            'description': dept.description
        }
    })

@csrf_exempt
@login_required
def edit_department(request, pk):
    dept = get_object_or_404(Department, pk=pk)

    name = request.POST.get('name', '').strip()
    code = request.POST.get('code', '').strip()
    description = request.POST.get('description', '').strip()

    # ✅ Required validation
    if not name and not code:
        return JsonResponse({'success': False, 'error': 'নাম ও কোড আবশ্যক'}, status=400)
    elif not name:
        return JsonResponse({'success': False, 'error': 'বিভাগের নাম আবশ্যক'}, status=400)
    elif not code:
        return JsonResponse({'success': False, 'error': 'বিভাগের কোড আবশ্যক'}, status=400)

    # ✅ Unique validation (excluding current dept)
    if Department.objects.filter(name=name).exclude(pk=dept.pk).exists():
        return JsonResponse({'success': False, 'error': f"নাম '{name}' অন্য বিভাগে ব্যবহৃত হয়েছে"}, status=400)

    if Department.objects.filter(code=code).exclude(pk=dept.pk).exists():
        return JsonResponse({'success': False, 'error': f"কোড '{code}' অন্য বিভাগে ব্যবহৃত হয়েছে"}, status=400)

    # ✅ Try–except to catch DB-level error
    try:
        dept.name = name
        dept.code = code
        dept.description = description
        dept.save()
    except Exception as e:
        return JsonResponse({'success': False, 'error': f"❌ ডাটাবেস সমস্যা: {str(e)}"}, status=500)

    return JsonResponse({
        'success': True,
        'message': f"✅ বিভাগ '{dept.name}' আপডেট হয়েছে",
        'department': {
            'id': dept.id,
            'name': dept.name,
            'code': dept.code,
            'description': dept.description
        }
    })
@csrf_exempt
@login_required
def delete_department(request, pk): 
    dept = Department.objects.filter(pk=pk).first()
    if not dept:
        return JsonResponse({'success': False, 'error': 'বিভাগ পাওয়া যায়নি'}, status=404)
    
    dept.delete()
    return JsonResponse({'success': True})

@login_required
def department_list_json(request):
    departments = Department.objects.all().order_by('name')
    data = [{
        'id': d.id,
        'name': d.name,
        'code': d.code,
        'description': d.description or ''
    } for d in departments]
    return JsonResponse({'departments': data})

# Module Group Management
# Module Management
@csrf_exempt
@login_required
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

@login_required
def module_list(request):
    with open(settings.BASE_DIR / 'static/icons.json', 'r') as f:
        icon_list = json.load(f)
        
    modules = Module.objects.select_related('group', 'parent').order_by('order')
    groups = ModuleGroup.objects.all()
    actions = ActionType.objects.all()
    return render(request, 'accounts/module_list.html', {
        'modules': modules,
        'module_groups': groups,
        'icon_list': icon_list,
        'actions': actions
    })

@login_required
def module_create(request):
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save()
            form.save_m2m()
            return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
def module_form_handler(request, module_id=None):
    if request.method == 'POST':
        instance = get_object_or_404(Module, pk=module_id) if module_id else None
        form = ModuleForm(request.POST, instance=instance)
        print(form.errors)

        if form.is_valid():
            module = form.save()
            return JsonResponse({
                'success': True,
                'created': instance is None,
                'module': {
                    'id': module.id,
                    'name': module.name
                }
            })
        else:
            # ✅ Simplified error dict for JS
            errors = {field: [str(e) for e in errs] for field, errs in form.errors.items()}
            return JsonResponse({'success': False, 'error': errors}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

@require_POST
@login_required
def module_delete(request, module_id):
    if request.method == 'POST':
        module = get_object_or_404(Module, id=module_id)
        module.delete()
    return redirect('module_list')

@login_required
def module_group_list_view(request):
    groups = ModuleGroup.objects.all().order_by('order')

    context = {
        'module_groups': groups,
        'can_edit': has_permission(request, 'accounts:module_group_list', 'edit'),
        'can_delete': has_permission(request, 'accounts:module_group_delete', 'delete'),
    }
    return render(request, 'accounts/modals/module_group.html', context)   

@csrf_exempt
@login_required
def module_group_save_ajax(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)

    group_id = request.POST.get("id")
    name = request.POST.get("name", "").strip()
    icon = request.POST.get("icon", "").strip()
    order = request.POST.get("order", "0")

    if not name:
        return JsonResponse({"success": False, "error": "Group name is required"}, status=400)

    try:
        order = int(order)
    except ValueError:
        return JsonResponse({"success": False, "error": "Order must be a number"}, status=400)

    if group_id:
        group = ModuleGroup.objects.filter(id=group_id).first()
        if not group:
            return JsonResponse({"success": False, "error": "Group not found"}, status=404)
        group.name = name
        group.icon = icon
        group.order = order
        group.updated_by = request.user
        group.save()
        return JsonResponse({"success": True, "created": False, "group": {
            "id": group.id, "name": group.name, "icon": group.icon, "order": group.order
        }})
    else:
        group = ModuleGroup.objects.create(
            name=name,
            icon=icon,
            order=order,
            created_by=request.user
        )
        return JsonResponse({"success": True, "created": True, "group": {
            "id": group.id, "name": group.name, "icon": group.icon, "order": group.order
        }})

@csrf_exempt
@login_required
def module_group_delete_ajax(request, id):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)

    group = get_object_or_404(ModuleGroup, pk=id)
    group.delete()
    return JsonResponse({"success": True, "message": f"Group '{group.name}' deleted successfully"})
