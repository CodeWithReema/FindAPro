"""
Admin configuration for providers app.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import ServiceCategory, ServiceProvider, FavoriteProvider, ProviderImage, QuoteRequest


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    """Admin for ServiceCategory model."""
    
    list_display = ['name', 'slug', 'icon', 'provider_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']


class ProviderImageInline(admin.TabularInline):
    """Inline admin for provider gallery images."""
    model = ProviderImage
    extra = 1
    fields = ['image', 'caption', 'is_featured', 'order']


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    """Admin for ServiceProvider model."""
    
    list_display = [
        'name', 'category', 'city', 'state', 'pricing_range',
        'is_verified_badge', 'is_available_now', 'accepts_emergency', 'is_active', 'average_rating', 'review_count', 'created_at'
    ]
    list_filter = ['category', 'is_verified', 'is_active', 'is_featured', 'is_available_now', 'accepts_emergency', 'pricing_range', 'state']
    search_fields = ['name', 'description', 'skills', 'email', 'city']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['-created_at']
    readonly_fields = ['average_rating', 'review_count', 'created_at', 'updated_at']
    inlines = [ProviderImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'slug', 'tagline', 'description')
        }),
        ('Category & Skills', {
            'fields': ('category', 'skills')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'website')
        }),
        ('Location', {
            'fields': ('address', 'city', 'state', 'zip_code')
        }),
        ('Business Details', {
            'fields': ('pricing_range', 'years_experience')
        }),
        ('Media', {
            'fields': ('image', 'logo')
        }),
        ('Status', {
            'fields': ('is_verified', 'is_active', 'is_featured')
        }),
        ('Emergency & Availability', {
            'fields': ('is_available_now', 'accepts_emergency', 'emergency_rate_info')
        }),
        ('Statistics (Read Only)', {
            'fields': ('average_rating', 'review_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_verified_badge(self, obj):
        if obj.is_verified:
            return format_html('<span style="color: green;">✓ Verified</span>')
        return format_html('<span style="color: gray;">—</span>')
    is_verified_badge.short_description = 'Verified'


@admin.register(ProviderImage)
class ProviderImageAdmin(admin.ModelAdmin):
    """Admin for ProviderImage model."""
    
    list_display = ['provider', 'caption', 'is_featured', 'order', 'created_at']
    list_filter = ['is_featured', 'created_at']
    search_fields = ['provider__name', 'caption']
    ordering = ['provider', '-is_featured', 'order']
    raw_id_fields = ['provider']


@admin.register(FavoriteProvider)
class FavoriteProviderAdmin(admin.ModelAdmin):
    """Admin for FavoriteProvider model."""
    
    list_display = ['user', 'provider', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email', 'provider__name']
    ordering = ['-created_at']
    raw_id_fields = ['user', 'provider']


@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    """Admin for QuoteRequest model."""
    
    list_display = ['title', 'user', 'provider', 'status', 'budget', 'quote_amount', 'created_at']
    list_filter = ['status', 'timeline', 'budget', 'created_at']
    search_fields = ['title', 'description', 'user__username', 'user__email', 'provider__name']
    ordering = ['-created_at']
    raw_id_fields = ['user', 'provider']
    readonly_fields = ['created_at', 'updated_at', 'quoted_at']
    
    fieldsets = (
        ('Request Info', {
            'fields': ('user', 'provider', 'title', 'description', 'status')
        }),
        ('Project Details', {
            'fields': ('timeline', 'budget', 'preferred_contact', 'phone')
        }),
        ('Service Location', {
            'fields': ('service_address', 'service_city', 'service_zip')
        }),
        ('Quote Response', {
            'fields': ('quote_amount', 'quote_message', 'quoted_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

