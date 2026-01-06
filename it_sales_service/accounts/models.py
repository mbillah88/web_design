# accounts/models.py
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    is_protected = models.BooleanField(default=False)  # Optional: prevent deletion
    modules = models.ManyToManyField('Module', through='Permission')

    def __str__(self):
        return self.name

    def sync_to_group(self):
        group, created = Group.objects.get_or_create(name=self.name)
        # Optional: assign model-level permissions here
        return group

class ActionType(models.Model):
    key = models.CharField(max_length=20, unique=True)       # e.g. 'access'
    name_bn = models.CharField(max_length=50)                # e.g. 'প্রবেশাধিকার'
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name_bn

class ModuleGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, default='bi-folder')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

class Module(models.Model):
    name = models.CharField(max_length=100)
    url_name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, default='bi-circle')
    is_visible = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    group = models.ForeignKey(ModuleGroup, null=True, blank=True, on_delete=models.SET_NULL, related_name='modules')
    is_accordion = models.BooleanField(default=False)  # Optional control
    actions = models.ManyToManyField(ActionType, related_name='modules')

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

class Permission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    action = models.ForeignKey(ActionType, on_delete=models.CASCADE)
    is_allowed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('role', 'module', 'action')

class Permission1(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    can_access = models.BooleanField(default=False)
    can_create = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    class Meta:
        unique_together = ('role', 'module')
        
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


