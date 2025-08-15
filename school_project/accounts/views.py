from django.shortcuts import render
# accounts/views.py
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import LoginForm
# accounts/views.py# accounts/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    role = request.user.role
    return render(request, f'accounts/{role}_dashboard.html')

@login_required
def admin_dashboard(request):
    return render(request, 'accounts/admin_dashboard.html')

@login_required
def teacher_dashboard(request):
    return render(request, 'accounts/teacher_dashboard.html')

@login_required
def student_dashboard(request):
    return render(request, 'accounts/student_dashboard.html')

def student_list(request):
    students = Student.objects.all()
    return render(request, 'students/student_list.html', {'students': students})
# views.py
@login_required
def student_profile(request):
    student = get_object_or_404(Student, user=request.user)
    return render(request, 'accounts/student_profile.html', {'student': student})

def login_view(request):
    form = LoginForm(request, data=request.POST or None)
    if form.is_valid():
        user = form.get_user()
        login(request, user)
        if user.role == 'admin':
            return redirect('admin_dashboard')
        elif user.role == 'teacher':
            return redirect('teacher_dashboard')
        elif user.role == 'student':
            return redirect('student_dashboard')
    return render(request, 'accounts/login.html', {'form': form})

# Create your views here.
