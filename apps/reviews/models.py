"""
Models for provider reviews.
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class ProviderReview(models.Model):
    """Review for a service provider."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    provider = models.ForeignKey(
        'providers.ServiceProvider',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Rating from 1 to 5 stars'
    )
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField()
    
    # Optional fields
    would_recommend = models.BooleanField(default=True)
    service_date = models.DateField(null=True, blank=True)
    
    # Helpful votes
    helpful_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Provider Review'
        verbose_name_plural = 'Provider Reviews'
        ordering = ['-created_at']
        # Prevent duplicate reviews
        unique_together = ['user', 'provider']
    
    def __str__(self):
        return f"{self.user.username} - {self.provider.name} ({self.rating}★)"
    
    def get_rating_stars(self):
        """Return list of star values for template rendering."""
        return ['full' if i < self.rating else 'empty' for i in range(5)]

