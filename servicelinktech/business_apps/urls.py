from django.urls import path
from . import views

app_name = "slt"
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('new_sales/', views.new_sales, name='new_sales'),
    path('category_list', views.item_category_list, name='category_list'),
    path('category_list/category_add', views.item_category_add, name='category_add'),
    
]