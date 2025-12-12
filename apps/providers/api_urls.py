"""
API URL patterns for providers.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'providers', api_views.ServiceProviderViewSet, basename='provider')
router.register(r'categories', api_views.ServiceCategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
]

