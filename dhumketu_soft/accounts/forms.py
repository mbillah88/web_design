from django import forms
from django.contrib.auth import get_user_model
from .models import Role, Module, CustomUser

User = get_user_model()

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name']

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['name', 'url_name', 'icon']

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'phone', 'address', 'profile_image']
