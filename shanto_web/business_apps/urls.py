from django.urls import path
from . import views

app_name = "business_apps"
urlpatterns = [
    path('', views.dashboard, name='business'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('product/', views.product, name='product'),
    path('product/product_add', views.product_add, name='product_add'),
    path('product/<int:pk>', views.product_details, name='product_details'),
    path('product/<int:pk>/product_update', views.product_update, name='product_update'),
    #path('image/<int:pk>/delete/', views.image_delete, name='image_delete'),
    
    path('category', views.category, name='category'),
    path('category/category_add', views.category_add, name='category_add'),
    path('category/<int:pk>', views.category_details, name='category_details'),
    path('category/<int:pk>/category_update', views.category_update, name='category_update'),
    #path('image/<int:pk>/delete/', views.image_delete, name='image_delete'),
   
    path('brands', views.brands, name='brands'),
    path('brands/new_brand', views.new_brand, name='new_brand'),
    path('brands/<int:pk>/brand_update', views.brand_update, name='brand_update'),
    #path('image/<int:pk>/delete/', views.image_delete, name='image_delete'),
    
    path('clients', views.clients, name='clients'),
    path('clients/clients_new', views.clients_new, name='clients_new'),
    path('clients/<int:pk>/clients_update', views.clients_update, name='clients_update'),
    #path('image/<int:pk>/delete/', views.image_delete, name='image_delete'),

    path('supplier', views.supplier, name='supplier'),
    path('supplier/supplier_new', views.supplier_new, name='supplier_new'),
    path('supplier/<int:pk>/supplier_update', views.supplier_update, name='supplier_update'),
    #path('image/<int:pk>/delete/', views.image_delete, name='image_delete'),

    path('sales/', views.sales, name='sales'),
    path('sales/sales_new', views.sales_new, name='sales_new'),
    path('sales/<int:pk>/sales_update', views.sales_update, name='sales_update'),
    
    path('purchase/', views.purchase, name='purchase'),
    path('purchase/purchase_new', views.purchase_new, name='purchase_new'),
    path('purchase/<int:pk>/purchase_update', views.purchase_update, name='purchase_update'),
    
]