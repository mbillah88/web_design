from django.contrib import admin
from django.urls import path
from . import views

app_name = "shop_apps"
urlpatterns = [
    path("", views.home, name="home"),
    path("product/", views.product, name="product"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
        
]