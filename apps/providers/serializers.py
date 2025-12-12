"""
Serializers for providers API.
"""

from rest_framework import serializers
from .models import ServiceCategory, ServiceProvider


class ServiceCategorySerializer(serializers.ModelSerializer):
    """Serializer for service categories."""
    
    provider_count = serializers.ReadOnlyField()
    
    class Meta:
        model = ServiceCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 
            'image', 'provider_count'
        ]


class ServiceProviderListSerializer(serializers.ModelSerializer):
    """Serializer for provider list view."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    location = serializers.ReadOnlyField()
    
    class Meta:
        model = ServiceProvider
        fields = [
            'id', 'name', 'slug', 'tagline', 'category', 'category_name',
            'city', 'state', 'zip_code', 'location', 'pricing_range',
            'image', 'is_verified', 'average_rating', 'review_count'
        ]


class ServiceProviderDetailSerializer(serializers.ModelSerializer):
    """Serializer for provider detail view."""
    
    category = ServiceCategorySerializer(read_only=True)
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    skills_list = serializers.ReadOnlyField()
    location = serializers.ReadOnlyField()
    
    class Meta:
        model = ServiceProvider
        fields = [
            'id', 'name', 'slug', 'description', 'tagline',
            'category', 'skills', 'skills_list',
            'email', 'phone', 'website',
            'address', 'city', 'state', 'zip_code', 'location',
            'pricing_range', 'years_experience',
            'image', 'logo', 'is_verified', 'is_featured',
            'average_rating', 'review_count',
            'created_at', 'updated_at'
        ]

