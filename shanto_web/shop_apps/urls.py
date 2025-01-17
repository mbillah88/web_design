from django.contrib import admin
from django.urls import path
from . import views

app_name = "shop_apps"
urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
     
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
    
]