# accounts/views.py
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from .forms import ProfileForm, UserCreationForm
from .models import CustomUser
from accounts.decorators import role_required

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')  # ✅ Redirect to role-based dashboard
        else:
            return render(request, 'login.html', {'error': 'ইউজারনেম বা পাসওয়ার্ড ভুল'})
    return render(request, 'login.html')
@login_required
def dashboard(request):
    print("User:", request.user)
    print("Role:", getattr(request.user, 'role', 'Not found'))

    context = {
        'role': getattr(request.user, 'role', None),
        'username': request.user.username,
        'full_name': request.user.get_full_name(),
        'age': request.user.get_age() or 'Not calculated'

    }
    return render(request, 'dashboard/dashboard.html', context)
def logout_view(request):
    logout(request)
    return redirect('login')
@login_required
def profile_detail(request):
    return render(request, 'accounts/profile_detail.html', {'user': request.user})

@login_required
@role_required(['admin'])
def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'নতুন ইউজার সফলভাবে যুক্ত হয়েছে।')
            return redirect('admin_dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})
@login_required
@role_required(['admin'])
def add_user(request):
    form = UserCreationForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('user_list')
    return render(request, 'accounts/add_user.html', {'form': form})
@login_required
@role_required(['admin'])
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    form = ProfileForm(request.POST or None, request.FILES or None, instance=user)
    if form.is_valid():
        form.save()
        messages.success(request, "✅ ইউজারের তথ্য সফলভাবে সংরক্ষণ করা হয়েছে।")
        return redirect('user_list')
    else:
        messages.error(request, "❌ তথ্য সংরক্ষণে সমস্যা হয়েছে। অনুগ্রহ করে আবার চেষ্টা করুন।")
    return render(request, 'accounts/profile_form.html', {'form': form})

@login_required
@role_required(['admin'])
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('user_list')
    return redirect('user_list')

@login_required
def profile_update(request):
    user = request.user
    form = ProfileForm(request.POST or None, request.FILES or None, instance=user)
    if form.is_valid():
        form.save()
        return redirect('profile_detail')
    return render(request, 'accounts/profile_form.html', {'form': form})
@login_required
def user_list(request):
    users = CustomUser.objects.filter(is_active=True).order_by('-date_joined')
    return render(request, 'accounts/user_list.html', {'users': users})
