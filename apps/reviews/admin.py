"""
Admin configuration for reviews app.
"""

from django.contrib import admin
from .models import ProviderReview


@admin.register(ProviderReview)
class ProviderReviewAdmin(admin.ModelAdmin):
    """Admin for ProviderReview model."""
    
    list_display = ['user', 'provider', 'rating', 'would_recommend', 'helpful_count', 'created_at']
    list_filter = ['rating', 'would_recommend', 'created_at']
    search_fields = ['user__username', 'user__email', 'provider__name', 'comment']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Review Details', {
            'fields': ('user', 'provider', 'rating', 'title', 'comment')
        }),
        ('Additional Info', {
            'fields': ('would_recommend', 'service_date', 'helpful_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

