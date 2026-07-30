"""
URL configuration for merkatolima_frontend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from marketplace import views as marketplace_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/upload-images/', marketplace_views.upload_images, name='upload_images'),
    path('', include('marketplace.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)