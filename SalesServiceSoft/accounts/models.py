from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('technician', 'Technician'),
        ('sales', 'Sales'),
        ('manager', 'Manager'),
        ('viewer', 'Viewer'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(default=timezone.now)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'role']
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    def __str__(self):
        return self.username
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()    
    def get_short_name(self):
        return self.first_name if self.first_name else self.username
    def save(self, *args, **kwargs):
        if not self.role or self.role.strip() == '':
            self.role = 'viewer'
        super().save(*args, **kwargs)
    def has_perm(self, perm, obj=None):
        if self.is_superuser:
            return True
        return super().has_perm(perm, obj)
    def has_module_perms(self, app_label):
        if self.is_superuser:
            return True
        return super().has_module_perms(app_label)
        
    def get_profile_image_url(self):
        if self.profile_image:
            return self.profile_image.url
        return '/static/img/default_profile.png'
    def get_phone_number(self):
        return self.phone if self.phone else 'No phone number provided'
    def get_address(self):
        return self.address if self.address else 'No address provided'
    def get_age(self):
        from datetime import date
        if self.date_of_birth:
            today = date.today()
            age = today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
            return age
        return None
    def is_active_user(self):
        return self.is_active and not self.is_superuser
    def deactivate_user(self):
        self.is_active = False
        self.save()
    def activate_user(self):
        self.is_active = True
        self.save()
    def get_last_login_formatted(self):
        if self.last_login:
            return self.last_login.strftime('%Y-%m-%d %H:%M:%S')
        return 'Never logged in'
    def get_date_joined_formatted(self):
        return self.date_joined.strftime('%Y-%m-%d %H:%M:%S') if self.date_joined else 'Date not available'
    def get_user_info(self):
        return {
            'username': self.username,
            'email': self.email,
            'role': self.get_role_display(),
            'phone': self.get_phone_number(),
            'address': self.get_address(),
            'date_of_birth': self.date_of_birth.strftime('%Y-%m-%d') if self.date_of_birth else 'Not provided',
            'profile_image_url': self.get_profile_image_url(),
            'is_active': self.is_active,
            'date_joined': self.get_date_joined_formatted(),
            'last_login': self.get_last_login_formatted(),
        }
    def get_permissions(self):
        if self.is_superuser:
            return ['*']
        permissions = super().get_all_permissions()
        return list(permissions) if permissions else []
    def __repr__(self):
        return f"<CustomUser(username={self.username}, role={self.role})>"