from django.urls import path
from . import views

urlpatterns = [
    path('phome/', views.public_home, name='public_home'),
    path('business/', views.sidebar, name='sidebar'),
    path('admin', views.ulogin, name='ulogin'),
    path('', views.business, name='business'),
    
]