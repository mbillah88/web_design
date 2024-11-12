from django.urls import path
from . import views

urlpatterns = [
    path('phome/', views.public_home, name='public_home'),
    path('', views.sidebar, name='sidebar'),
    path('login/', views.ulogin, name='ulogin'),
    path('business/', views.business, name='business'),
    
]