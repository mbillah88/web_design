# routine/views.py
from django.shortcuts import render
from .models import Routine

def view_routine(request):
    routines = Routine.objects.filter(class_name='৯ম')
    return render(request, 'routine/view_routine.html', {'routines': routines})
