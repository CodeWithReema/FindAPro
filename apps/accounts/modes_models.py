"""
Models for multi-mode profile system: Freelance and Skill Swap modes.
"""

from django.db import models
from django.conf import settings
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator


class Skill(models.Model):
    """Reusable skills model for freelance and skill swap."""
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    category = models.CharField(
        max_length=50,
        choices=[
            ('design', 'Design'),
            ('development', 'Development'),
            ('marketing', 'Marketing'),
            ('writing', 'Writing'),
            ('business', 'Business'),
            ('technical', 'Technical'),
            ('creative', 'Creative'),
            ('other', 'Other'),
        ],
        default='other'
    )
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Icon class or emoji')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'accounts'
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'
        ordering = ['category', 'name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('accounts:skill_detail', kwargs={'slug': self.slug})


class FreelanceListing(models.Model):
    """Freelance mode listing for project-based work."""
    
    PRICING_TYPE_CHOICES = [
        ('hourly', 'Hourly Rate'),
        ('project', 'Project-Based'),
        ('both', 'Both'),
    ]
    
    AVAILABILITY_CHOICES = [
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('unavailable', 'Unavailable'),
    ]
    
    # Owner
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='freelance_listing'
    )
    
    # Basic Info
    title = models.CharField(max_length=200, help_text='Professional title or tagline')
    bio = models.TextField(help_text='Professional bio/description')
    headline = models.CharField(max_length=255, blank=True, help_text='Short headline')
    
    # Skills & Expertise
    skills = models.ManyToManyField(
        Skill,
        related_name='freelance_listings',
        help_text='Skills and expertise tags'
    )
    expertise_tags = models.CharField(
        max_length=500,
        blank=True,
        help_text='Comma-separated additional tags'
    )
    
    # Pricing
    pricing_type = models.CharField(
        max_length=20,
        choices=PRICING_TYPE_CHOICES,
        default='both'
    )
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text='Hourly rate in USD'
    )
    project_rate_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text='Minimum project rate'
    )
    project_rate_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text='Maximum project rate'
    )
    currency = models.CharField(max_length=3, default='USD')
    
    # Portfolio
    portfolio_url = models.URLField(blank=True, help_text='Link to portfolio website')
    github_url = models.URLField(blank=True, help_text='GitHub profile URL')
    linkedin_url = models.URLField(blank=True, help_text='LinkedIn profile URL')
    behance_url = models.URLField(blank=True, help_text='Behance/Dribbble URL')
    
    # Availability
    availability_status = models.CharField(
        max_length=20,
        choices=AVAILABILITY_CHOICES,
        default='available'
    )
    availability_notes = models.TextField(
        blank=True,
        help_text='Additional availability information'
    )
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'accounts'
        verbose_name = 'Freelance Listing'
        verbose_name_plural = 'Freelance Listings'
        ordering = ['-is_featured', '-created_at']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.title}"
    
    def get_absolute_url(self):
        return reverse('accounts:freelance_detail', kwargs={'pk': self.pk})
    
    @property
    def skills_list(self):
        """Return skills as a list."""
        return list(self.skills.all())
    
    @property
    def expertise_tags_list(self):
        """Return expertise tags as a list."""
        if self.expertise_tags:
            return [tag.strip() for tag in self.expertise_tags.split(',') if tag.strip()]
        return []


class FreelancePortfolioItem(models.Model):
    """Portfolio items for freelance listings (images, links, case studies)."""
    
    listing = models.ForeignKey(
        FreelanceListing,
        on_delete=models.CASCADE,
        related_name='portfolio_items'
    )
    
    TYPE_CHOICES = [
        ('image', 'Image'),
        ('link', 'Link'),
        ('case_study', 'Case Study'),
    ]
    
    item_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='image')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # For images
    image = models.ImageField(
        upload_to='freelance/portfolio/',
        blank=True,
        null=True
    )
    
    # For links
    url = models.URLField(blank=True, help_text='Portfolio link URL')
    
    # For case studies
    case_study_content = models.TextField(
        blank=True,
        help_text='Case study content (markdown supported)'
    )
    
    # Ordering
    order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'accounts'
        verbose_name = 'Portfolio Item'
        verbose_name_plural = 'Portfolio Items'
        ordering = ['-is_featured', 'order', '-created_at']
    
    def __str__(self):
        return f"{self.listing.user.full_name} - {self.title}"


class SkillSwapListing(models.Model):
    """Skill swap mode listing for bartering services."""
    
    # Owner
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='skill_swap_listing'
    )
    
    # Bio
    bio = models.TextField(
        help_text='Tell others about yourself and what you\'re looking for in skill swaps'
    )
    
    # Skills Offered (ManyToMany)
    skills_offered = models.ManyToManyField(
        Skill,
        related_name='swap_listings_offered',
        help_text='Skills you can offer to others'
    )
    
    # Skills Wanted (ManyToMany)
    skills_wanted = models.ManyToManyField(
        Skill,
        related_name='swap_listings_wanted',
        help_text='Skills you want to learn or receive'
    )
    
    # Additional skills (text fields for flexibility)
    additional_skills_offered = models.CharField(
        max_length=500,
        blank=True,
        help_text='Comma-separated additional skills you offer'
    )
    additional_skills_wanted = models.CharField(
        max_length=500,
        blank=True,
        help_text='Comma-separated additional skills you want'
    )
    
    # Credit System
    credits_earned = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text='Total credits earned (1 hour = 1 credit)'
    )
    credits_spent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text='Total credits spent'
    )
    
    # Location (for local swaps)
    location_preference = models.CharField(
        max_length=100,
        blank=True,
        help_text='Preferred location for swaps (city, state or "remote")'
    )
    accepts_remote = models.BooleanField(
        default=True,
        help_text='Accept remote skill swaps'
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'accounts'
        verbose_name = 'Skill Swap Listing'
        verbose_name_plural = 'Skill Swap Listings'
        ordering = ['-is_verified', '-created_at']
    
    def __str__(self):
        return f"{self.user.full_name} - Skill Swap"
    
    def get_absolute_url(self):
        return reverse('accounts:skill_swap_detail', kwargs={'pk': self.pk})
    
    @property
    def credits_balance(self):
        """Calculate current credit balance."""
        return self.credits_earned - self.credits_spent
    
    def get_available_balance(self):
        """Get available balance (excluding escrow)."""
        from .credit_service import CreditTransactionService
        return CreditTransactionService.get_available_balance(self.user)
    
    def get_pending_credits(self):
        """Get credits held in escrow."""
        from .credit_service import CreditTransactionService
        return CreditTransactionService.get_pending_credits(self.user)
    
    @property
    def skills_offered_list(self):
        """Return all skills offered as a list."""
        skills = list(self.skills_offered.all())
        if self.additional_skills_offered:
            skills.extend([s.strip() for s in self.additional_skills_offered.split(',') if s.strip()])
        return skills
    
    @property
    def skills_wanted_list(self):
        """Return all skills wanted as a list."""
        skills = list(self.skills_wanted.all())
        if self.additional_skills_wanted:
            skills.extend([s.strip() for s in self.additional_skills_wanted.split(',') if s.strip()])
        return skills


class SkillSwapJob(models.Model):
    """Track skill swap jobs from request to completion."""
    
    STATUS_CHOICES = [
        ('posted', 'Posted'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('disputed', 'Disputed'),
    ]
    
    # Participants
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='swap_jobs_requested',
        help_text='User requesting the service'
    )
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='swap_jobs_provided',
        null=True,
        blank=True,
        help_text='User providing the service'
    )
    
    # Job details
    title = models.CharField(max_length=200)
    description = models.TextField()
    skill_needed = models.ForeignKey(
        Skill,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='swap_jobs',
        help_text='Skill needed for this job'
    )
    hours_required = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0.5)],
        help_text='Number of hours required (1 hour = 1 credit)'
    )
    
    # Status and dates
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='posted'
    )
    posted_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # Completion confirmation
    requester_confirmed = models.BooleanField(default=False)
    provider_confirmed = models.BooleanField(default=False)
    
    # Escrow
    credits_in_escrow = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text='Credits held in escrow until completion'
    )
    
    # Dispute resolution
    dispute_reason = models.TextField(blank=True)
    dispute_resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='disputes_resolved',
        help_text='Admin who resolved the dispute'
    )
    dispute_resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    class Meta:
        app_label = 'accounts'
        verbose_name = 'Skill Swap Job'
        verbose_name_plural = 'Skill Swap Jobs'
        ordering = ['-posted_at']
        indexes = [
            models.Index(fields=['requester', 'status']),
            models.Index(fields=['provider', 'status']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    @property
    def credits_required(self):
        """Credits required for this job (same as hours)."""
        return self.hours_required
    
    @property
    def is_completed(self):
        """Check if job is completed and confirmed by both parties."""
        return (
            self.status == 'completed' and
            self.requester_confirmed and
            self.provider_confirmed
        )


class SkillCredit(models.Model):
    """Track skill swap credits (time-banking: 1 hour = 1 credit)."""
    
    TRANSACTION_TYPE_CHOICES = [
        ('earned', 'Earned'),
        ('spent', 'Spent'),
        ('bonus', 'Bonus'),
        ('adjustment', 'Adjustment'),
        ('refund', 'Refund'),
        ('escrow_hold', 'Escrow Hold'),
        ('escrow_release', 'Escrow Release'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Participants
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='credits_given',
        null=True,
        blank=True,
        help_text='User who provided the service (null for system transactions)'
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='credits_received',
        help_text='User receiving/earning credits'
    )
    
    # Related job (if applicable)
    job = models.ForeignKey(
        SkillSwapJob,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='credit_transactions',
        help_text='Associated skill swap job'
    )
    
    # Transaction details
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPE_CHOICES
    )
    credits = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Number of credits (hours)'
    )
    
    # Swap details
    skill_swapped = models.ForeignKey(
        Skill,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Skill that was swapped'
    )
    description = models.TextField(
        help_text='Description of the transaction'
    )
    swap_date = models.DateField(
        null=True,
        blank=True,
        help_text='Date when the swap occurred'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Verification
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='credits_verified',
        help_text='Admin or user who verified this transaction'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Admin notes
    admin_notes = models.TextField(
        blank=True,
        help_text='Admin notes for adjustments or disputes'
    )
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Expiration (optional)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Credit expiration date (if applicable)'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'accounts'
        verbose_name = 'Skill Credit'
        verbose_name_plural = 'Skill Credits'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['to_user', 'status', '-created_at']),
            models.Index(fields=['transaction_type', 'status']),
        ]
    
    def __str__(self):
        if self.from_user:
            return f"{self.from_user.full_name} → {self.to_user.full_name}: {self.credits} credits ({self.get_transaction_type_display()})"
        return f"System → {self.to_user.full_name}: {self.credits} credits ({self.get_transaction_type_display()})"
    
    @property
    def is_expired(self):
        """Check if credit has expired."""
        if self.expires_at:
            from django.utils import timezone
            return timezone.now() > self.expires_at
        return False
    
    def save(self, *args, **kwargs):
        """Update user credit totals when credit is approved."""
        is_new = self.pk is None
        old_status = None
        
        if not is_new:
            old_instance = SkillCredit.objects.get(pk=self.pk)
            old_status = old_instance.status
        
        super().save(*args, **kwargs)
        
        # Only process if status changed to approved
        if self.status == 'approved' and old_status != 'approved':
            self._update_user_credits()
    
    def _update_user_credits(self):
        """Update user credit totals based on transaction type."""
        if not hasattr(self.to_user, 'skill_swap_listing'):
            return
        
        listing = self.to_user.skill_swap_listing
        
        if self.transaction_type == 'earned':
            listing.credits_earned += self.credits
        elif self.transaction_type == 'spent':
            listing.credits_spent += self.credits
        elif self.transaction_type == 'bonus':
            listing.credits_earned += self.credits
        elif self.transaction_type == 'refund':
            # Refund adds back to earned (or reduces spent)
            listing.credits_spent = max(0, listing.credits_spent - self.credits)
        elif self.transaction_type == 'adjustment':
            # Adjustments can be positive or negative
            if self.credits > 0:
                listing.credits_earned += self.credits
            else:
                listing.credits_spent += abs(self.credits)
        elif self.transaction_type == 'escrow_hold':
            # Escrow hold doesn't change balance, just tracks
            pass
        elif self.transaction_type == 'escrow_release':
            # Release from escrow transfers credits
            if self.from_user and hasattr(self.from_user, 'skill_swap_listing'):
                self.from_user.skill_swap_listing.credits_spent += self.credits
                self.from_user.skill_swap_listing.save()
            listing.credits_earned += self.credits
        
        listing.save()
