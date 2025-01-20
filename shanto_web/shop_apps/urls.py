from django.contrib import admin
from django.urls import path
from . import views

app_name = "shop_apps"
urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
     
    path('product/', views.product, name='product'),
    path('product/<int:pk>', views.product_details, name='product_details'),
        
]