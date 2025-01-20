
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.generic.base import TemplateView

urlpatterns = [
    #Project Url...
    path("", TemplateView.as_view(template_name="public_home.html"), name="home"),
    path("product/", TemplateView.as_view(template_name="product.html"), name="product"),
    path("service/", TemplateView.as_view(template_name="service.html"), name="service"),
    path("blog/", TemplateView.as_view(template_name="blog.html"), name="blog"),
    path("about/", TemplateView.as_view(template_name="about.html"), name="about"),

    #Apps Url...
    path("slt/", include('business_apps.urls'), name="slt"),

    #Super Admin Url...
    path("dj-admin/", admin.site.urls),
    #Custom Admin  Url...
    path("accounts/", include("django.contrib.auth.urls")), 

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)