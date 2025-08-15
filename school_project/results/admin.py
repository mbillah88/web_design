from django.contrib import admin

# Register your models here.
# results/admin.py
from .models import Subject, Exam, Result
admin.site.register(Subject)
admin.site.register(Exam)
admin.site.register(Result)
