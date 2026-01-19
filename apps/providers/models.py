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
    is_draft = models.BooleanField(default=True, help_text='Profile is in draft mode and not visible to public')
    
    # Approval & Verification
    APPROVAL_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_review', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    ]
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default='draft'
    )
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True)
    submitted_for_review_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, help_text='Reason for rejection if applicable')
    
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
    
    def calculate_completion_percentage(self):
        """Calculate profile completion percentage based on filled fields."""
        total_fields = 0
        filled_fields = 0
        
        # Basic Info (5 fields)
        fields_to_check = [
            ('name', self.name),
            ('category', self.category_id),
            ('description', self.description),
            ('skills', self.skills),
            ('tagline', self.tagline),
        ]
        for field_name, field_value in fields_to_check:
            total_fields += 1
            if field_value:
                filled_fields += 1
        
        # Contact & Location (7 fields)
        fields_to_check = [
            ('email', self.email),
            ('phone', self.phone),
            ('website', self.website),
            ('address', self.address),
            ('city', self.city),
            ('state', self.state),
            ('zip_code', self.zip_code),
        ]
        for field_name, field_value in fields_to_check:
            total_fields += 1
            if field_value:
                filled_fields += 1
        
        # Business Details (2 fields)
        total_fields += 1
        if self.pricing_range:
            filled_fields += 1
        total_fields += 1
        if self.years_experience and self.years_experience > 0:
            filled_fields += 1
        
        # Media (2 fields)
        total_fields += 1
        if self.logo:
            filled_fields += 1
        total_fields += 1
        if self.image:
            filled_fields += 1
        
        # Emergency settings (2 fields)
        total_fields += 1
        if self.accepts_emergency:
            filled_fields += 1
        total_fields += 1
        if self.emergency_rate_info:
            filled_fields += 1
        
        # Business hours (check if exists)
        total_fields += 1
        if hasattr(self, 'business_hours') and self.business_hours:
            filled_fields += 1
        
        # Service areas (check if exists)
        total_fields += 1
        if hasattr(self, 'service_areas') and self.service_areas.exists():
            filled_fields += 1
        
        if total_fields == 0:
            return 0
        
        percentage = (filled_fields / total_fields) * 100
        return round(percentage, 1)
    
    @property
    def completion_percentage(self):
        """Property to get completion percentage."""
        return self.calculate_completion_percentage()
    
    def can_submit(self):
        """Check if profile can be submitted (minimum 50% completion)."""
        return self.completion_percentage >= 50


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


class BusinessHours(models.Model):
    """Business hours schedule for service providers."""
    
    provider = models.OneToOneField(
        ServiceProvider,
        on_delete=models.CASCADE,
        related_name='business_hours'
    )
    
    # Monday
    monday_open = models.TimeField(null=True, blank=True)
    monday_close = models.TimeField(null=True, blank=True)
    monday_closed = models.BooleanField(default=False)
    
    # Tuesday
    tuesday_open = models.TimeField(null=True, blank=True)
    tuesday_close = models.TimeField(null=True, blank=True)
    tuesday_closed = models.BooleanField(default=False)
    
    # Wednesday
    wednesday_open = models.TimeField(null=True, blank=True)
    wednesday_close = models.TimeField(null=True, blank=True)
    wednesday_closed = models.BooleanField(default=False)
    
    # Thursday
    thursday_open = models.TimeField(null=True, blank=True)
    thursday_close = models.TimeField(null=True, blank=True)
    thursday_closed = models.BooleanField(default=False)
    
    # Friday
    friday_open = models.TimeField(null=True, blank=True)
    friday_close = models.TimeField(null=True, blank=True)
    friday_closed = models.BooleanField(default=False)
    
    # Saturday
    saturday_open = models.TimeField(null=True, blank=True)
    saturday_close = models.TimeField(null=True, blank=True)
    saturday_closed = models.BooleanField(default=False)
    
    # Sunday
    sunday_open = models.TimeField(null=True, blank=True)
    sunday_close = models.TimeField(null=True, blank=True)
    sunday_closed = models.BooleanField(default=False)
    
    # Notes
    notes = models.TextField(blank=True, help_text='Additional notes about availability')
    
    class Meta:
        verbose_name = 'Business Hours'
        verbose_name_plural = 'Business Hours'
    
    def __str__(self):
        return f"Business Hours - {self.provider.name}"
    
    def get_day_hours(self, day_name):
        """Get hours for a specific day."""
        open_field = f"{day_name.lower()}_open"
        close_field = f"{day_name.lower()}_close"
        closed_field = f"{day_name.lower()}_closed"
        
        if getattr(self, closed_field):
            return "Closed"
        
        open_time = getattr(self, open_field)
        close_time = getattr(self, close_field)
        
        if open_time and close_time:
            return f"{open_time.strftime('%I:%M %p')} - {close_time.strftime('%I:%M %p')}"
        
        return "Not set"


class ServiceArea(models.Model):
    """Service areas/coverage zones for providers."""
    
    provider = models.ForeignKey(
        ServiceProvider,
        on_delete=models.CASCADE,
        related_name='service_areas'
    )
    zip_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    radius_miles = models.PositiveIntegerField(
        default=25,
        help_text='Service radius in miles from this location'
    )
    is_primary = models.BooleanField(
        default=False,
        help_text='Primary service location'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Service Area'
        verbose_name_plural = 'Service Areas'
        ordering = ['-is_primary', 'city', 'state']
    
    def __str__(self):
        return f"{self.city}, {self.state} {self.zip_code} ({self.radius_miles} miles) - {self.provider.name}"
    
    def save(self, *args, **kwargs):
        # If this is marked as primary, unmark others
        if self.is_primary:
            ServiceArea.objects.filter(
                provider=self.provider,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class ProviderCertification(models.Model):
    """Certifications and licenses for service providers."""
    
    provider = models.ForeignKey(
        ServiceProvider,
        on_delete=models.CASCADE,
        related_name='certifications'
    )
    name = models.CharField(max_length=200, help_text='e.g., "Licensed Electrician"')
    issuing_organization = models.CharField(max_length=200, blank=True)
    license_number = models.CharField(max_length=100, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    verification_document = models.FileField(
        upload_to='certifications/',
        blank=True,
        null=True,
        help_text='Upload verification document'
    )
    is_verified = models.BooleanField(
        default=False,
        help_text='Admin verified certification'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Provider Certification'
        verbose_name_plural = 'Provider Certifications'
        ordering = ['-is_verified', '-issue_date']
    
    def __str__(self):
        return f"{self.name} - {self.provider.name}"
    
    @property
    def is_expired(self):
        """Check if certification is expired."""
        if self.expiry_date:
            from django.utils import timezone
            return timezone.now().date() > self.expiry_date
        return False
