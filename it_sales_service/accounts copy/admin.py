from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Role, Module, Permission, Department, Profile

# 🔐 CustomUser Admin
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email')
    ordering = ('username',)
    
    readonly_fields = ('last_login', 'date_joined')  # ✅ এই লাইন যোগ করো
    
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('ব্যক্তিগত তথ্য', {'fields': ('first_name', 'last_name')}),
        ('রোল ও অনুমতি', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('তারিখ', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )

# 🎛️ Role Admin
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

# 🧩 Module Admin@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'url_name', 'parent', 'is_visible', 'order')
    list_filter = ('is_visible', 'parent')
    search_fields = ('name', 'url_name')

# 🔐 Permission Admin
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('role', 'module', 'can_access', 'can_create', 'can_edit', 'can_delete')
    list_filter = ('role', 'module')
    search_fields = ('role__name', 'module__name')
    ordering = ('role', 'module')

# 🏢 Department Admin
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')
    ordering = ('name',)

# 👤 Profile Admin
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'first_name', 'last_name', 'designation',
        'department', 'mobile_number', 'emergency_contact', 'emergency_phone'
    )
    list_filter = ('department',)
    search_fields = (
        'user__username', 'first_name', 'last_name',
        'designation', 'mobile_number', 'emergency_contact'
    )
    ordering = ('user',)

# ✅ Register all models
try:
    admin.site.unregister(CustomUser)
except admin.sites.NotRegistered:
    pass

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(Permission, PermissionAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Profile, ProfileAdmin)

# 🎨 Bangla Branding
admin.site.site_header = "🔧 প্রশাসনিক প্যানেল"
admin.site.site_title = "Bangla SaaS Admin"
admin.site.index_title = "ড্যাশবোর্ডে স্বাগতম"
