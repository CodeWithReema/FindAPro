"""
Serializers for reviews API.
"""

from rest_framework import serializers
from .models import ProviderReview


class ProviderReviewSerializer(serializers.ModelSerializer):
    """Serializer for provider reviews."""
    
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_avatar = serializers.ImageField(source='user.avatar', read_only=True)
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    
    class Meta:
        model = ProviderReview
        fields = [
            'id', 'user', 'user_name', 'user_avatar',
            'provider', 'provider_name',
            'rating', 'title', 'comment',
            'would_recommend', 'service_date',
            'helpful_count', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'helpful_count', 'created_at']


class CreateReviewSerializer(serializers.ModelSerializer):
    """Serializer for creating reviews."""
    
    class Meta:
        model = ProviderReview
        fields = ['provider', 'rating', 'title', 'comment', 'would_recommend', 'service_date']
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value
    
    def validate(self, data):
        user = self.context['request'].user
        provider = data.get('provider')
        
        # Check if user already reviewed this provider
        if ProviderReview.objects.filter(user=user, provider=provider).exists():
            raise serializers.ValidationError(
                "You have already reviewed this provider. You can edit your existing review."
            )
        
        return data
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

