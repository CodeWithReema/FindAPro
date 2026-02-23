"""
Custom User model for FindAPro.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Extended user model with additional fields."""
    
    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('provider', 'Service Provider'),
    ]
    
    email = models.EmailField(unique=True)
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='customer'
    )
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True
    )
    bio = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    
    # Profile Mode Activation Flags
    is_freelancer_active = models.BooleanField(
        default=False,
        help_text='Freelance mode is active'
    )
    is_skill_swap_active = models.BooleanField(
        default=False,
        help_text='Skill swap mode is active'
    )
    
    # Active Mode Selection (for UI context)
    active_mode = models.CharField(
        max_length=20,
        choices=[
            ('provider', 'Service Provider'),
            ('freelance', 'Freelance'),
            ('skill_swap', 'Skill Swap'),
        ],
        default='provider',
        blank=True,
        help_text='Currently active mode for UI context'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email or self.username
    
    @property
    def full_name(self):
        """Return user's full name or username."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    @property
    def is_provider(self):
        """Check if user is a service provider."""
        return self.user_type == 'provider'
    
    @property
    def is_customer(self):
        """Check if user is a customer."""
        return self.user_type == 'customer'
    
    @property
    def has_provider_profile(self):
        """Check if user has a provider profile."""
        return hasattr(self, 'provider_profile')
    
    @property
    def has_freelance_listing(self):
        """Check if user has a freelance listing."""
        return hasattr(self, 'freelance_listing')
    
    @property
    def has_skill_swap_listing(self):
        """Check if user has a skill swap listing."""
        return hasattr(self, 'skill_swap_listing')
    
    @property
    def active_modes(self):
        """Return list of active modes."""
        modes = []
        if self.has_provider_profile and self.provider_profile.is_active and not self.provider_profile.is_draft:
            modes.append('provider')
        if self.is_freelancer_active and self.has_freelance_listing:
            modes.append('freelance')
        if self.is_skill_swap_active and self.has_skill_swap_listing:
            modes.append('skill_swap')
        return modes
    
    @property
    def total_skill_credits(self):
        """Calculate total skill credits earned."""
        if hasattr(self, 'skill_swap_listing'):
            return self.skill_swap_listing.credits_earned
        return 0


# Import modes models so Django discovers them
from .modes_models import (
    Skill, FreelanceListing, FreelancePortfolioItem,
    SkillSwapListing, SkillCredit
)

# Import matching models so Django discovers them
from .matching_models import Match, MatchHistory

# Import credit system models so Django discovers them
from .modes_models import SkillSwapJob
