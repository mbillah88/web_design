from django.urls import path
from . import views

urlpatterns = [
    path('roles/', views.role_list, name='role_list'),
    path('roles/add/', views.role_add, name='role_add'),
    path('permissions/matrix/', views.permission_matrix, name='permission_matrix'),
    path('permissions/toggle/', views.toggle_permission, name='toggle_permission'),
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.user_add, name='user_add'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:pk>/view/', views.user_view, name='user_view'),
    path('profile/', views.profile_view, name='profile_view'),

]
