from django.urls import path
from . import views

urlpatterns = [
    path('matrix/', views.permission_matrix, name='permission_matrix'),
    path('toggle/', views.toggle_permission, name='toggle_permission'),
]
