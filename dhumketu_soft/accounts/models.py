from django.contrib.auth.models import AbstractUser
from django.db import models



class Role(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Module(models.Model):
    name = models.CharField(max_length=100)
    url_name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name

class PermissionMatrix(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    can_access = models.BooleanField(default=False)

    class Meta:
        unique_together = ('role', 'module')

class CustomUser(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.username