"""
URL patterns for reviews app - Template views.
"""

from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('create/<slug:provider_slug>/', views.create_review, name='create_review'),
    path('edit/<int:review_id>/', views.edit_review, name='edit_review'),
    path('delete/<int:review_id>/', views.delete_review, name='delete_review'),
    path('helpful/<int:review_id>/', views.mark_helpful, name='mark_helpful'),
]

