# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'অ্যাডমিন'),
        ('teacher', 'শিক্ষক'),
        ('student', 'শিক্ষার্থী'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

# models.py
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll = models.CharField(max_length=10)
    class_name = models.CharField(max_length=20)
    photo = models.ImageField(upload_to='student_photos/')
    phone = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return f"{self.user.first_name} ({self.roll})"
