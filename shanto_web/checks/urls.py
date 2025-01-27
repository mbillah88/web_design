from django.urls import path
from . import views
app_name: "checks"
urlpatterns = [
    path('add_sales_item/', views.add_sales_item, name='add_sales_item'),
    path('search_products/', views.search_products, name='search_products'),
]
