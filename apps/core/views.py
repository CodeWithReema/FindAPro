"""
Views for core app - Homepage and utilities.
"""

from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Avg, Count

from apps.providers.models import ServiceCategory, ServiceProvider


class HomeView(TemplateView):
    """Homepage view."""
    
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get active categories with provider counts
        context['categories'] = ServiceCategory.objects.filter(
            is_active=True
        ).annotate(
            num_providers=Count('providers', filter=models.Q(providers__is_active=True))
        )[:8]
        
        # Get featured providers
        context['featured_providers'] = ServiceProvider.objects.filter(
            is_active=True,
            is_featured=True
        ).select_related('category').annotate(
            avg_rating=Avg('reviews__rating')
        )[:6]
        
        # Get top rated providers
        context['top_providers'] = ServiceProvider.objects.filter(
            is_active=True
        ).select_related('category').annotate(
            avg_rating=Avg('reviews__rating'),
            num_reviews=Count('reviews')
        ).filter(num_reviews__gte=1).order_by('-avg_rating')[:4]
        
        # Stats for hero section
        context['stats'] = {
            'providers': ServiceProvider.objects.filter(is_active=True).count(),
            'categories': ServiceCategory.objects.filter(is_active=True).count(),
            'reviews': sum(p.review_count for p in ServiceProvider.objects.all()),
        }
        
        return context


# Import models for the Q object
from django.db import models


class AboutView(TemplateView):
    """About page view."""
    template_name = 'core/about.html'


class ContactView(TemplateView):
    """Contact page view."""
    template_name = 'core/contact.html'


def custom_404(request, exception):
    """Custom 404 error page."""
    return render(request, 'errors/404.html', status=404)


def custom_500(request):
    """Custom 500 error page."""
    return render(request, 'errors/500.html', status=500)

