# students/models.py
from django.db import models
from accounts.models import User

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
