# accounts/urls.py
from django.urls import path
from accounts.views import *

app_name = 'accounts'

urlpatterns = [
    # 🔐 Authentication
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # 📊 Dashboard
    path('dashboard/', dashboard, name='dashboard'),

    # 🛡️ Role Management
    path('roles/', role_list, name='role_list'),
    path('roles/create/', role_form, name='role_create'),
    path('roles/edit/<int:role_id>/', role_form, name='role_edit'),
    path('roles/delete/<int:role_id>/', role_delete, name='role_delete'),
    path('roles/clone/<int:source_role_id>/', role_clone_view, name='role_clone'),    

    # 🛡️ Permission Management
    path('permissions/matrix/', permission_matrix_view, name='permission_matrix'),
    path('permissions/update/', update_permission, name='update_permission'),
    path('permissions/grant_all/', grant_all_permissions_view, name='grant_all_permissions'),
    path('permissions/revoke_all/', revoke_all_permissions_view, name='revoke_all_permissions'),

    # 👤 User Management
    path('users/', user_list, name='user_list'),
    path('users/create/', user_form_handler, name='user_create'),
    path('users/edit/<int:user_id>/', user_form_handler, name='user_edit'),
    path('users/delete/<int:user_id>/', user_delete, name='user_delete'),
    path('password-modal/', password_modal_view, name='password_modal'),
    path('users/password/<int:user_id>/', user_password_update, name='user_password_update'),

    # 📁 Profile Management
    path('profile/<int:user_id>/', profile_view_or_edit, name='profile_view'),
    path('departments/add/', add_department, name='add_department'),
    path('departments/edit/<int:pk>/', edit_department, name='edit_department'),
    path('departments/delete/<int:pk>/', delete_department, name='delete_department'),
    path('departments/list-json/', department_list_json, name='department_list_json'),


    # Module ম্যানেজমেন্ট
    path('modules/sync/ajax/', sync_modules_ajax, name='module_sync'),
    path('modules/', module_list, name='module_list'),
    path('modules/form/', module_form_handler, name='module_create'),
    path('modules/form/<int:module_id>/', module_form_handler, name='module_update'),
    path('modules/delete/<int:module_id>/', module_delete, name='module_delete'),
    
    # ModuleGroup ম্যানেজমেন্ট    
    path('module-groups/', module_group_list_view, name='module_group_list'),
    path('module-groups/save/', module_group_save_ajax, name='module_group_save'),
    path('module-groups/delete/<int:id>/', module_group_delete_ajax, name='module_group_delete'),

]
