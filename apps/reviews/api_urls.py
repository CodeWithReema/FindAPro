"""
API URL patterns for reviews.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'reviews', api_views.ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
]

