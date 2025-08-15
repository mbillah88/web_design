# routine/urls.py
from django.urls import path
from .views import view_routine

urlpatterns = [
    path('', view_routine, name='view_routine'),
]
