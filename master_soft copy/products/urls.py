from django.urls import path
from products.views import *

app_name = 'products'

urlpatterns = [
    # 🔹 Product CRUD
    path('', product_list, name='product_list'),
    path('create/', create_product, name='create'),
    path('<int:product_id>/edit/', edit_product, name='edit'),
    path('<int:product_id>/delete/', delete_product, name='delete'),
    path('<int:product_id>/json/', product_json, name='json'),
    path('check-barcode/', check_barcode, name='check_barcode'),
    path('products/search/', product_search, name='product_search'),

    # 🔹 Category
    path('category/', category_list, name='category_list'),
    path('category/create/', create_category, name='category_create'),
    path('category/<int:pk>/edit/', edit_category, name='category_edit'),
    path('category/<int:pk>/delete/', delete_category, name='category_delete'),
    path('category/<int:category_id>/json/', category_json, name='category_json'),


    # 🔹 Brand
    path('brand/', brand_list, name='brand_list'),
    path('brand/create/', create_brand, name='create_brand'),
    path('brand/<int:brand_id>/edit/', edit_brand, name='edit_brand'),
    path('brand/<int:brand_id>/delete/', delete_brand, name='delete_brand'),
    path('brand/<int:brand_id>/json/', brand_list_json, name='brand_list_json'),

    # 🔹 Unit
    path('unit/', unit_list, name='unit_list'),
    path('unit/create/', create_unit, name='create_unit'),
    path('unit/<int:unit_id>/edit/', edit_unit, name='edit_unit'),
    path('unit/<int:unit_id>/delete/', delete_unit, name='delete_unit'),
    path('unit/list-json/', unit_list_json, name='unit_list_json'),
    path('unit/<int:unit_id>/json/', unit_json, name='unit_json'),


    # 🔹 Warranty
    path('warranty/', warranty_list, name='warranty_list'),
    path('warranty/create/', create_warranty, name='create_warranty'),
    path('warranty/<int:warranty_id>/edit/', edit_warranty, name='edit_warranty'),
    path('warranty/<int:warranty_id>/delete/', delete_warranty, name='delete_warranty'),
    path('warranty/<int:warranty_id>/json/', warranty_json, name='warranty_json'),
    path('warranty/json/list/', warranty_list_json, name='warranty_list_json'),

    # Product Serial...
    path('product/<int:product_id>/serial/list-json/', serial_list_json, name='serial_list_json'),
    path('serial/add/', create_serial, name='create_serial'),
    path('serial/<int:serial_id>/edit/', edit_serial, name='edit_serial'),
    path('serial/<int:serial_id>/delete/', delete_serial, name='delete_serial'),

    # Purchase
    path('purchase/', purchase_list, name='purchase_list'),
    path('purchase/create/', purchase_create, name='purchase_create'),
    path('purchase/<int:pk>/edit/', purchase_edit, name='purchase_edit'),# urls.py
    path("purchase/<int:pk>/update/", purchase_update, name="purchase_update"),

    path('purchase/<int:pk>/delete/', purchase_delete, name='purchase_delete'),
    path("purchase/<int:pk>/summary/", purchase_summary, name="purchase_summary"),

    # Purchase Payments
    path("purchase/payments/", payment_list, name="payment_list"),
    path('purchase/payment/', purchase_payment, name='purchase_payment'),
    path("purchase/payment/<int:pk>/update/", update_payment, name="update_payment"),
    path("purchase/payment/<int:pk>/delete/", delete_payment, name="delete_payment"),
    path("purchase/payment-methods/", payment_method_list, name="payment_method_list"),
    path('purchase/payment/bulk-create/', bulk_create_payment, name='bulk_create_payment'),

      # 🔹 Refund
    path("refund/", process_refund, name="process_refund"),
    path("refund/list/", refund_list, name="refund_list"),
    path("refund/reason-stats/", refund_reason_stats, name="refund_reason_stats"),

    # 🔹 Inventory
    path("stock-in/", stock_in, name="stock_in"),

    # 🔹 Supplier Ledger
    path('supplier/create/', create_supplier_ajax, name='create_supplier_ajax'),
    path("supplier/search/", supplier_search, name="supplier_search"),
    path("supplier/ledger/update/", update_ledger, name="update_ledger"),
    path("supplier/<int:pk>/detail/", supplier_detail, name="supplier_detail"),
    path("supplier/<int:supplier_id>/refund-ledger/", supplier_refund_ledger, name="supplier_refund_ledger"),

]