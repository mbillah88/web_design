# routine/models.py
from django.db import models
from accounts.models import CustomUser

class Routine(models.Model):
    class_name = models.CharField(max_length=20)
    day = models.CharField(max_length=10)
    time = models.CharField(max_length=20)
    subject = models.CharField(max_length=50)
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
