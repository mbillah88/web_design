
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.generic.base import TemplateView

urlpatterns = [
    #path("", include('business_apps.urls')),
    path("", TemplateView.as_view(template_name="public_home.html"), name="home"),
    path("slt/", include('business_apps.urls'), name="slt"),
    path("dj-admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")), 
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
