from django.urls import path
from . import views

urlpatterns = [
    path('', views.public_home, name='public_home'),
    path('business/', views.sidebar, name='sidebar'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin', views.ulogin, name='ulogin'),
    path('phome/', views.business, name='business'),
    
]