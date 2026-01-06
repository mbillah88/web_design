from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

# Create your models here.

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    is_protected = models.BooleanField(default=False)  # Optional: prevent deletion
    modules = models.ManyToManyField('Module', through='Permission')
    is_active = models.BooleanField(default=1)

    def __str__(self):
        return self.name

    def sync_to_group(self):
        group, created = Group.objects.get_or_create(name=self.name)
        # Optional: assign model-level permissions here
        return group
class ModuleGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, default='bi-folder')
    icon_unicode = models.CharField(max_length=10, blank=True, null=True)  # Optional: Unicode for icons
    order = models.PositiveIntegerField(default=0)

class Module(models.Model):
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=100, blank=True, null=True)  # ✅ Add this line    
    url_name = models.CharField(max_length=100, unique=True)
    class_name = models.CharField(max_length=100, unique=True, blank=True, null=True)  # Optional: for JS/CSS targeting
    icon = models.CharField(max_length=50, default='bi-circle')
    icon_unicode = models.CharField(max_length=10, blank=True, null=True)  # Optional: Unicode for icons
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')    
    group = models.ForeignKey(ModuleGroup, on_delete=models.SET_NULL, null=True, related_name='modules')
    actions = models.ManyToManyField('ActionType', related_name='modules')
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)
    is_header = models.BooleanField(default=False)  # Header visibility ✅
    is_default = models.BooleanField(default=False)  # Default module ✅

class ActionType(models.Model):
    key = models.CharField(max_length=20, unique=True)
    name_bn = models.CharField(max_length=50)
    order = models.PositiveIntegerField(default=0)

class Permission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    action = models.ForeignKey(ActionType, on_delete=models.CASCADE)
    is_allowed = models.BooleanField(default=False)
    created_by = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_permissions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_permissions')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('role', 'module', 'action')
     
class Department(models.Model):
    name = models.CharField("Department", max_length=100, unique=True)
    code = models.CharField("Department Code", max_length=20, unique=True)
    description = models.TextField("Descriptions", blank=True)

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

class CustomUser(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(auto_now=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_protected = models.BooleanField(default=True)  # 🔐 সুরক্ষিত ইউজার

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.role:
            group = self.role.sync_to_group()
            self.groups.set([group])  # ✅ Sync Django group with role

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')

    # Personal Info
    first_name = models.CharField("নামের প্রথম অংশ", max_length=30, blank=True)
    last_name = models.CharField("নামের শেষ অংশ", max_length=30, blank=True)
    date_of_birth = models.DateField("জন্ম তারিখ", null=True, blank=True)

    # Contact Info
    phone_number = models.CharField("ফোন নম্বর", max_length=15, blank=True)
    mobile_number = models.CharField("মোবাইল নম্বর", max_length=15, blank=True)
    address = models.TextField("ঠিকানা", blank=True)

    # Emergency Info
    emergency_contact = models.CharField("জরুরি যোগাযোগ", max_length=100, blank=True)
    emergency_phone = models.CharField("জরুরি ফোন", max_length=15, blank=True)

    # Organizational Info
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="বিভাগ")
    designation = models.CharField("পদবি", max_length=100, blank=True)

    # Profile Image
    profile_image = models.ImageField("প্রোফাইল ছবি", upload_to='profile_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class AuditLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=50)
    target_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='target_logs')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} → {self.action} → {self.target_user.username}"
