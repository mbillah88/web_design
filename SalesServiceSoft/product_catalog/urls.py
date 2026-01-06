from django.urls import path
from product_catalog.views import (product_list, product_edit, product_add, add_unit_ajax, product_delete,
                unit_list, unit_add, unit_edit, unit_delete,
                category_list, category_add, category_edit, category_delete,
                brand_list, brand_add, brand_edit, brand_delete)

urlpatterns = [
    # Product
    path('products/', product_list, name='product_list'),
    path('products/add/', product_add, name='product_add'),
    path('products/edit/<int:pk>/', product_edit, name='product_edit'),
    path('products/delete/<int:pk>/', product_delete, name='product_delete'),

    # Unit
    path('units/', unit_list, name='unit_list'),
    path('units/add/', unit_add, name='unit_add'),
    path('units/edit/<int:pk>/', unit_edit, name='unit_edit'),
    path('units/delete/<int:pk>/', unit_delete, name='unit_delete'),
    path('units/add/ajax/', add_unit_ajax, name='add_unit_ajax'),

    # Category
    path('categories/', category_list, name='category_list'),
    path('categories/add/', category_add, name='category_add'),
    path('categories/edit/<int:pk>/', category_edit, name='category_edit'),
    path('categories/delete/<int:pk>/', category_delete, name='category_delete'),

    # Brand
    path('brands/', brand_list, name='brand_list'),
    path('brands/add/', brand_add, name='brand_add'),
    path('brands/edit/<int:pk>/', brand_edit, name='brand_edit'),
    path('brands/delete/<int:pk>/', brand_delete, name='brand_delete'),
]
