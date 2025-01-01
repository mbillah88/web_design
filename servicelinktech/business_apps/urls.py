from django.urls import path
from . import views

app_name = "slt"
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('nsales/', views.new_sales, name='new_sales'),
    
]