from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("shop_apps.urls")),
    path("business/", include("business_apps.urls")),
    path("admin/", admin.site.urls),
]
