from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        'username', 'email', 'role', 'is_active', 'is_staff',
        'get_age', 'last_login', 'date_joined'
    )
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'phone')
    ordering = ('-date_joined',)

    fieldsets = (
        ('প্রাথমিক তথ্য', {
            'fields': ('username', 'email', 'password', 'role')
        }),
        ('ব্যক্তিগত তথ্য', {
            'fields': ('first_name', 'last_name', 'phone', 'address', 'date_of_birth', 'profile_image')
        }),
        ('স্ট্যাটাস ও অনুমতি', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('সিস্টেম তথ্য', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'password1', 'password2'),
        }),
    )
