"""
API Views for reviews.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ProviderReview
from .serializers import ProviderReviewSerializer, CreateReviewSerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Custom permission to only allow owners to edit reviews."""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class ReviewViewSet(viewsets.ModelViewSet):
    """
    API endpoint for reviews.
    
    list: GET /api/reviews/
    create: POST /api/reviews/ (authenticated)
    retrieve: GET /api/reviews/<id>/
    update: PUT /api/reviews/<id>/ (owner only)
    destroy: DELETE /api/reviews/<id>/ (owner only)
    """
    
    queryset = ProviderReview.objects.select_related('user', 'provider')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateReviewSerializer
        return ProviderReviewSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by provider
        provider_id = self.request.query_params.get('provider')
        if provider_id:
            queryset = queryset.filter(provider_id=provider_id)
        
        # Filter by user
        user_id = self.request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by rating
        rating = self.request.query_params.get('rating')
        if rating:
            queryset = queryset.filter(rating=rating)
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def helpful(self, request, pk=None):
        """Mark a review as helpful."""
        review = self.get_object()
        review.helpful_count += 1
        review.save()
        
        return Response({
            'success': True,
            'helpful_count': review.helpful_count
        })
    
    @action(detail=False, methods=['get'])
    def my_reviews(self, request):
        """Get current user's reviews."""
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        reviews = self.get_queryset().filter(user=request.user)
        serializer = ProviderReviewSerializer(reviews, many=True)
        return Response(serializer.data)

