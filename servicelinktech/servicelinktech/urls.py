
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.generic.base import TemplateView

urlpatterns = [
    #Project Url...
    path("", include('shop_apps.urls'), name="home"),
    #Apps Url...
    path("slt/", include('business_apps.urls'), name="slt"),

    #Super Admin Url...
    path("dj-admin/", admin.site.urls),
    #Custom Admin  Url...
    path("accounts/", include("django.contrib.auth.urls")), 

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)