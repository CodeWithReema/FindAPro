"""
Models for service providers and categories.
"""

from django.db import models
from django.conf import settings
from django.urls import reverse
from django.db.models import Avg


class ServiceCategory(models.Model):
    """Category for service providers."""
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Icon class name (e.g., fa-wrench)')
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Service Category'
        verbose_name_plural = 'Service Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('providers:category_detail', kwargs={'slug': self.slug})
    
    @property
    def provider_count(self):
        return self.providers.filter(is_active=True).count()


class ServiceProvider(models.Model):
    """Service provider profile."""
    
    PRICING_CHOICES = [
        ('$', 'Budget-friendly ($)'),
        ('$$', 'Moderate ($$)'),
        ('$$$', 'Premium ($$$)'),
        ('$$$$', 'Luxury ($$$$)'),
    ]
    
    # Owner (optional - can be linked to user)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='provider_profile'
    )
    
    # Basic Info
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    tagline = models.CharField(max_length=255, blank=True)
    
    # Category & Skills
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.PROTECT,
        related_name='providers'
    )
    skills = models.TextField(help_text='Comma-separated list of skills')
    
    # Contact Info
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    website = models.URLField(blank=True)
    
    # Location
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    
    # Business Details
    pricing_range = models.CharField(
        max_length=10,
        choices=PRICING_CHOICES,
        default='$$'
    )
    years_experience = models.PositiveIntegerField(default=0)
    
    # Images
    image = models.ImageField(upload_to='providers/', blank=True, null=True)
    logo = models.ImageField(upload_to='providers/logos/', blank=True, null=True)
    
    # Status
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Emergency & Availability
    is_available_now = models.BooleanField(default=False, help_text='Currently available for jobs')
    accepts_emergency = models.BooleanField(default=False, help_text='Accepts emergency/urgent requests')
    emergency_rate_info = models.CharField(
        max_length=100, 
        blank=True,
        help_text='Info about emergency rates (e.g., "25% premium for emergencies")'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Service Provider'
        verbose_name_plural = 'Service Providers'
        ordering = ['-is_featured', '-created_at']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('providers:provider_detail', kwargs={'slug': self.slug})
    
    @property
    def average_rating(self):
        """Calculate average rating from reviews."""
        avg = self.reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
        return round(avg, 1) if avg else 0
    
    @property
    def review_count(self):
        """Get total number of reviews."""
        return self.reviews.count()
    
    @property
    def skills_list(self):
        """Return skills as a list."""
        return [skill.strip() for skill in self.skills.split(',') if skill.strip()]
    
    @property
    def location(self):
        """Return formatted location."""
        return f"{self.city}, {self.state} {self.zip_code}"
    
    def get_rating_stars(self):
        """Return list of star values for template rendering."""
        rating = self.average_rating
        stars = []
        for i in range(1, 6):
            if rating >= i:
                stars.append('full')
            elif rating >= i - 0.5:
                stars.append('half')
            else:
                stars.append('empty')
        return stars


class FavoriteProvider(models.Model):
    """User's favorite/saved providers."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    provider = models.ForeignKey(
        ServiceProvider,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Favorite Provider'
        verbose_name_plural = 'Favorite Providers'
        unique_together = ['user', 'provider']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.provider.name}"


class ProviderImage(models.Model):
    """Portfolio/gallery images for service providers."""
    
    provider = models.ForeignKey(
        ServiceProvider,
        on_delete=models.CASCADE,
        related_name='gallery_images'
    )
    image = models.ImageField(upload_to='providers/gallery/')
    caption = models.CharField(max_length=255, blank=True)
    alt_text = models.CharField(max_length=255, blank=True, help_text='Description for accessibility')
    is_featured = models.BooleanField(default=False, help_text='Featured images appear first')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Provider Image'
        verbose_name_plural = 'Provider Images'
        ordering = ['-is_featured', 'order', '-created_at']
    
    def __str__(self):
        return f"{self.provider.name} - {self.caption or 'Image'}"
    
    def save(self, *args, **kwargs):
        # If this is marked as featured, unmark others
        if self.is_featured:
            ProviderImage.objects.filter(
                provider=self.provider,
                is_featured=True
            ).exclude(pk=self.pk).update(is_featured=False)
        super().save(*args, **kwargs)


class QuoteRequest(models.Model):
    """Quote request from user to provider."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('viewed', 'Viewed'),
        ('quoted', 'Quote Sent'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
    ]
    
    TIMELINE_CHOICES = [
        ('asap', 'As soon as possible'),
        ('this_week', 'This week'),
        ('next_week', 'Next week'),
        ('this_month', 'This month'),
        ('flexible', 'Flexible'),
    ]
    
    BUDGET_CHOICES = [
        ('under_100', 'Under $100'),
        ('100_500', '$100 - $500'),
        ('500_1000', '$500 - $1,000'),
        ('1000_5000', '$1,000 - $5,000'),
        ('5000_plus', '$5,000+'),
        ('not_sure', 'Not sure yet'),
    ]
    
    # Relationships
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quote_requests'
    )
    provider = models.ForeignKey(
        ServiceProvider,
        on_delete=models.CASCADE,
        related_name='quote_requests'
    )
    
    # Request Details
    title = models.CharField(max_length=200)
    description = models.TextField(help_text='Describe your project in detail')
    timeline = models.CharField(max_length=20, choices=TIMELINE_CHOICES, default='flexible')
    budget = models.CharField(max_length=20, choices=BUDGET_CHOICES, default='not_sure')
    is_emergency = models.BooleanField(default=False, help_text='Emergency/urgent request')
    
    # Contact Preferences
    preferred_contact = models.CharField(
        max_length=20,
        choices=[('email', 'Email'), ('phone', 'Phone'), ('either', 'Either')],
        default='either'
    )
    phone = models.CharField(max_length=20, blank=True)
    
    # Location
    service_address = models.CharField(max_length=255, blank=True)
    service_city = models.CharField(max_length=100, blank=True)
    service_zip = models.CharField(max_length=20, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Provider Response
    quote_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quote_message = models.TextField(blank=True)
    quoted_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Quote Request'
        verbose_name_plural = 'Quote Requests'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username} to {self.provider.name}"
    
    def get_absolute_url(self):
        return reverse('providers:quote_detail', kwargs={'pk': self.pk})
    
    @property
    def is_pending(self):
        return self.status == 'pending'
    
    @property
    def has_quote(self):
        return self.status == 'quoted' and self.quote_amount is not None
