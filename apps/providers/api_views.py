"""
API Views for providers.
"""

from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg

from .models import ServiceCategory, ServiceProvider
from .serializers import (
    ServiceCategorySerializer,
    ServiceProviderListSerializer,
    ServiceProviderDetailSerializer
)


class ServiceCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for service categories.
    
    list: GET /api/categories/
    retrieve: GET /api/categories/<id>/
    """
    
    queryset = ServiceCategory.objects.filter(is_active=True)
    serializer_class = ServiceCategorySerializer
    lookup_field = 'slug'


class ServiceProviderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for service providers.
    
    list: GET /api/providers/
    retrieve: GET /api/providers/<id>/
    
    Query Parameters:
    - category: Filter by category slug
    - city: Filter by city name
    - state: Filter by state
    - zip: Filter by zip code prefix
    - verified: Filter verified only (true/false)
    - pricing: Filter by pricing range ($, $$, $$$, $$$$)
    - search: Search in name, description, skills
    - ordering: Sort by field (-average_rating, name, -created_at)
    """
    
    queryset = ServiceProvider.objects.filter(is_active=True).select_related('category')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'skills', 'tagline']
    ordering_fields = ['name', 'created_at', 'pricing_range']
    ordering = ['-is_featured', '-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ServiceProviderDetailSerializer
        return ServiceProviderListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Filter by city
        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(city__icontains=city)
        
        # Filter by state
        state = self.request.query_params.get('state')
        if state:
            queryset = queryset.filter(state__icontains=state)
        
        # Filter by zip code
        zip_code = self.request.query_params.get('zip')
        if zip_code:
            queryset = queryset.filter(zip_code__startswith=zip_code)
        
        # Filter verified only
        verified = self.request.query_params.get('verified')
        if verified and verified.lower() == 'true':
            queryset = queryset.filter(is_verified=True)
        
        # Filter by pricing
        pricing = self.request.query_params.get('pricing')
        if pricing:
            queryset = queryset.filter(pricing_range=pricing)
        
        # Annotate with average rating for ordering
        queryset = queryset.annotate(avg_rating=Avg('reviews__rating'))
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured providers."""
        featured = self.get_queryset().filter(is_featured=True)[:6]
        serializer = ServiceProviderListSerializer(featured, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def top_rated(self, request):
        """Get top rated providers."""
        top_rated = self.get_queryset().order_by('-avg_rating')[:6]
        serializer = ServiceProviderListSerializer(top_rated, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get reviews for a specific provider."""
        provider = self.get_object()
        reviews = provider.reviews.select_related('user').order_by('-created_at')
        
        # Simple pagination
        page_size = 10
        page = int(request.query_params.get('page', 1))
        start = (page - 1) * page_size
        end = start + page_size
        
        from apps.reviews.serializers import ProviderReviewSerializer
        serializer = ProviderReviewSerializer(reviews[start:end], many=True)
        
        return Response({
            'count': reviews.count(),
            'results': serializer.data
        })

