"""
URL configuration for FindAPro project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # App URLs
    path('', include('apps.core.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('providers/', include('apps.providers.urls')),
    path('reviews/', include('apps.reviews.urls')),
    
    # API URLs
    path('api/', include('apps.providers.api_urls')),
    path('api/', include('apps.reviews.api_urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

