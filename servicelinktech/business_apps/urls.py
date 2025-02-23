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
    path('clients/clients_new_instance', views.clients_new_instance, name='clients_new_instance'),
    path('clients/<int:pk>/clients_update', views.clients_update, name='clients_update'),
    #path('image/<int:pk>/delete/', views.image_delete, name='image_delete'),

    path('supplier', views.supplier, name='supplier'),
    path('supplier/supplier_new', views.supplier_new, name='supplier_new'),
    path('supplier/add_supplier_new', views.add_supplier_new, name='add_supplier_new'),
    path('supplier/<int:pk>/supplier_update', views.supplier_update, name='supplier_update'),
    #path('image/<int:pk>/delete/', views.image_delete, name='image_delete'),

    path('sales/', views.sales, name='sales'),
    path('sales/sales_new', views.sales_new, name='sales_new'),
    path('sales/sales_update/<int:pk>/', views.sales_update, name='sales_update'),
    path('purchase/sales_due_form/<int:pk>/', views.sales_due_form, name='sales_due_form'),
    #path('sales/sales_due_pay/<int:pk>/', views.sales_due_pay, name='sales_due_pay'),
    path('sales/customer/<int:customer_pk>/', views.customer_details, name='customer_details'),
    path('sales/product_search/<int:pk>/', views.ItemListView.as_view(), name='ItemListView'),
    path('sales/sales_update/<int:sales_pk>/customer/<int:customer_pk>/', views.customer_details_sales, name='customer_details_sales_for_sales'),
    path('sales/sales_update/<int:sales_pk>/product_search/<int:product_search_pk>/', views.products_details_sales, name='products_details_sales_for_sales'),
    #path('sales/sales_update/<int:sales_pk>/item_delete_row/<int:row_id>/', views.item_delete_row, name='item_delete_row_for_sales'),
    
    path('sales/sales_invoice/<int:pk>/', views.sales_invoice, name='sales_invoice'),
    
    path('purchase/', views.purchase, name='purchase'),
    path('purchase/purchase_new', views.purchase_new, name='purchase_new'),
    path('purchase/purchase_update/<int:pk>/', views.purchase_update, name='purchase_update'),
    path('purchase/purchase_due_form/<int:pk>/', views.purchase_due_form, name='purchase_due_form'),
    path('purchase/supplier/<int:supplier_pk>/', views.supplier_detail, name='supplier_detail'),
    path('purchase/product_search/<int:pk>/', views.ItemListView.as_view(), name='ItemListView'),
    path('purchase/save_table_data', views.save_table_data, name='save_table_data'),
    path('purchase/success', views.success, name='success'),
    path('purchase/purchase_update/<int:purchase_pk>/supplier/<int:supplier_pk>/', views.supplier_details, name='supplier_details_for_purchase'),
    path('purchase/purchase_update/<int:purchase_pk>/pproducts_details/<int:product_search_pk>/', views.pproducts_details, name='pproducts_details_for_purchase'),
    path('purchase/purchase_update/<int:purchase_pk>/item_delete_row/<int:row_id>/', views.item_delete_row, name='item_delete_row_for_purchase'),
    
    path('purchase/purchase_invoice/<int:pk>/', views.purchase_invoice, name='purchase_invoice'),
    
    # Service ........
    path('service/', views.service, name='service'),

    # Settings Tools .... 
    path('settings/', views.settings, name='settings'),
    path('settings/tools_unit', views.tools_unit, name='tools_unit'),
    path('settings/<int:pk>/tools_unit_update', views.tools_unit_update, name='tools_unit_update'),
   
    # Reports Tools .... report_summary_daily
    path('reports/', views.reports, name='reports'),
    path('report_summary_daily/', views.report_summary_daily, name='report_summary_daily'),
]