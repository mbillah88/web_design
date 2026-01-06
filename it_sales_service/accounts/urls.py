# accounts/urls.py
from django.urls import path
from accounts.views import *

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard_view'),

    path('users/', user_list, name='user_list'),
    path('users/form/', user_form_handler, name='user_add'),
    path('users/form/<int:user_id>/', user_form_handler, name='user_edit'),
    path('users/delete/<int:user_id>/', user_delete, name='user_delete'),
    path('profile/view/<int:user_id>/', profile_view_page, name='profile_view'),
    path('profile/update/<int:user_id>/', profile_form_view, name='profile_update'),
    path('profile/add-department/', ajax_add_department, name='add_department'),

    # রোল ম্যানেজমেন্ট
    path('roles/', role_list, name='role_list'),
    path('roles/create/', role_create, name='role_create'),
    path('roles/delete/<int:role_id>/', role_delete, name='role_delete'),
    path('roles/edit/<int:role_id>/', role_edit, name='role_edit'),
    path('roles/clone/<int:role_id>/', clone_role, name='clone_role'),  # ✅ Role cloning
    path('roles/permissions/<int:role_id>/', role_permission_edit, name='role_permission_edit'),  # ✅ Granular permission UI

    # Module ম্যানেজমেন্ট
    path('modules/sync/ajax/', sync_modules_ajax, name='sync_modules_ajax'),
    path('modules/', module_list_view, name='module_list'),
    path('modules/form/', module_form_handler, name='module_add'),
    path('modules/form/<int:module_id>/', module_form_handler, name='module_edit'),
    path('modules/delete/<int:module_id>/', module_delete, name='module_delete'),
    
    # ModuleGroup ম্যানেজমেন্ট    
    path('module-groups/', module_group_list_view, name='module_group_list'),
    path('module-groups/save/', module_group_save_ajax, name='module_group_save'),
    path('module-groups/delete/<int:id>/', module_group_delete, name='delete_module_group'),

    path('module-groups/create/', module_group_create, name='module_group_create'),
    path('module-groups/update/<int:id>/', module_group_update, name='module_group_update'),
    path('module-groups/delete/<int:id>/', module_group_delete, name='module_group_delete'),
    path('module-groups/list/partial/', module_group_list_partial, name='module_group_list_partial'),
]
