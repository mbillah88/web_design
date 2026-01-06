# accounts/urls.py
from django.urls import path
from accounts.views import (
    login_view, logout_view, dashboard,
    profile_detail, profile_update,register_user,
    user_list, add_user,edit_user,delete_user
)

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),    
    path('register/', register_user, name='register'),
    path('profile/', profile_detail, name='profile_detail'),
    path('profile/edit/', profile_update, name='profile_update'),
    path('users/add/', add_user, name='add_user'),
    path('users/', user_list, name='user_list'),
    path('users/edit/<int:user_id>/', edit_user, name='edit_user'),
    path('users/delete/<int:user_id>/', delete_user, name='delete_user'),
]
