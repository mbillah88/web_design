from django.urls import path
from . import views

app_name = "slt"
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('sales/', views.sales, name='sales'),
    path('sales/new_sales/', views.new_sales, name='new_sales'),
    
    path('item/', views.item, name='item'),
    path('item/new_brands', views.item_add, name='item_add'),
    
    path('category', views.category, name='category'),
    path('category/category_add', views.category_add, name='category_add'),
   
    path('brands', views.brands, name='brands'),
    path('brands/new_brands', views.new_brands, name='new_brands'),
    
]