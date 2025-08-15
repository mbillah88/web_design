# accounts/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='ইউজারনেম')
    password = forms.CharField(widget=forms.PasswordInput, label='পাসওয়ার্ড')
