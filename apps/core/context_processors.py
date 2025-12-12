"""
Context processors for global template variables.
"""

from apps.providers.models import ServiceCategory


def categories_processor(request):
    """Add categories to all templates for navigation."""
    return {
        'nav_categories': ServiceCategory.objects.filter(is_active=True)[:6]
    }

