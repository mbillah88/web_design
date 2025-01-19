from django.contrib import admin
from django.urls import path
from . import views

app_name = "shop_apps"
urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
     
    path('store_product/', views.store_product, name='store_product'),
    path('store_product/<int:pk>', views.store_product_details, name='store_product_details'),
        
]