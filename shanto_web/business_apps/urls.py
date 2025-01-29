from django.urls import path
from . import views

app_name = "slt"
urlpatterns = [
    path('', views.dashboard, name='business'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('product/', views.product, name='product'),
    path('product/product_add', views.product_add, name='product_add'),
    path('product/<int:pk>', views.product_details, name='product_details'),
    path('product/<int:pk>/product_update', views.product_update, name='product_update'),
    path('product/product_ajax/', views.product_ajax, name='product_ajax'),
    path('product/product_search/', views.product_search, name='product_search'),
    path('product/<int:pk>/', views.item_detail, name='item_detail'),
    #path('api/my_model/<int:pk>/', views.MyModelDetail.as_view(), name='my_model_detail'),
    
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
    path('supplier/add_supplier_new', views.add_supplier_new, name='add_supplier_new'),
    path('supplier/<int:pk>/supplier_update', views.supplier_update, name='supplier_update'),
    #path('image/<int:pk>/delete/', views.image_delete, name='image_delete'),

    path('sales/', views.sales, name='sales'),
    path('sales/sales_new', views.sales_new, name='sales_new'),
    path('sales/<int:pk>/sales_update', views.sales_update, name='sales_update'),
    
    path('purchase/', views.purchase, name='purchase'),
    path('purchase/purchase_new', views.purchase_new, name='purchase_new'),
    path('purchase/purchase_new_order', views.purchase_order_process, name='purchase_order_process'),
    path('purchase/<int:pk>/purchase_update', views.purchase_update, name='purchase_update'),
    path('purchase/MyModelDetail/<int:pk>/', views.my_model_detail, name='my_model_detail'),
    
    # Settings Tools .... 
    path('settings/', views.settings, name='settings'),
    path('settings/tools_unit', views.tools_unit, name='tools_unit'),
    path('settings/<int:pk>/tools_unit_update', views.tools_unit_update, name='tools_unit_update'),
   
]