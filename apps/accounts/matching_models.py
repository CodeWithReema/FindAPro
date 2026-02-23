"""
Models for smart matching system.
"""

from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Match(models.Model):
    """Represents a potential match between two users."""
    
    MATCH_TYPE_CHOICES = [
        ('skill_swap', 'Skill Swap'),
        ('freelance_collab', 'Freelance Collaboration'),
        ('both', 'Both'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('viewed', 'Viewed'),
        ('interested', 'Interested'),
        ('connected', 'Connected'),
        ('not_interested', 'Not Interested'),
        ('expired', 'Expired'),
    ]
    
    # Users involved in the match
    user_a = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='matches_as_a'
    )
    user_b = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='matches_as_b'
    )
    
    # Match details
    match_type = models.CharField(
        max_length=20,
        choices=MATCH_TYPE_CHOICES,
        default='skill_swap'
    )
    compatibility_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Compatibility score (0-100)'
    )
    
    # Matching reasons
    skill_overlap_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Percentage of skills that overlap'
    )
    matching_skills = models.JSONField(
        default=list,
        help_text='List of skills that match'
    )
    geographic_proximity_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Geographic proximity score'
    )
    reputation_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Combined reputation/rating score'
    )
    availability_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Availability alignment score'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # User actions
    user_a_interested = models.BooleanField(default=False)
    user_b_interested = models.BooleanField(default=False)
    user_a_not_interested = models.BooleanField(default=False)
    user_b_not_interested = models.BooleanField(default=False)
    
    # Connection tracking
    connected_at = models.DateTimeField(null=True, blank=True)
    last_viewed_a = models.DateTimeField(null=True, blank=True)
    last_viewed_b = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'accounts'
        verbose_name = 'Match'
        verbose_name_plural = 'Matches'
        unique_together = ['user_a', 'user_b', 'match_type']
        ordering = ['-compatibility_score', '-created_at']
        indexes = [
            models.Index(fields=['user_a', 'status', '-compatibility_score']),
            models.Index(fields=['user_b', 'status', '-compatibility_score']),
        ]
    
    def __str__(self):
        return f"{self.user_a.full_name} ↔ {self.user_b.full_name} ({self.compatibility_score}%)"
    
    def get_absolute_url(self):
        return reverse('accounts:match_detail', kwargs={'pk': self.pk})
    
    @property
    def is_mutual_interest(self):
        """Check if both users are interested."""
        return self.user_a_interested and self.user_b_interested
    
    @property
    def is_connected(self):
        """Check if users have connected."""
        return self.status == 'connected' or self.is_mutual_interest
    
    def mark_viewed(self, user):
        """Mark match as viewed by a user."""
        if user == self.user_a:
            self.last_viewed_a = timezone.now()
            if self.status == 'pending':
                self.status = 'viewed'
        elif user == self.user_b:
            self.last_viewed_b = timezone.now()
            if self.status == 'pending':
                self.status = 'viewed'
        self.save()
    
    def mark_interested(self, user):
        """Mark user as interested in this match."""
        if user == self.user_a:
            self.user_a_interested = True
            self.user_a_not_interested = False
        elif user == self.user_b:
            self.user_b_interested = True
            self.user_b_not_interested = False
        
        if self.is_mutual_interest:
            self.status = 'connected'
            self.connected_at = timezone.now()
        
        self.save()
    
    def mark_not_interested(self, user):
        """Mark user as not interested in this match."""
        if user == self.user_a:
            self.user_a_not_interested = True
            self.user_a_interested = False
            self.status = 'not_interested'
        elif user == self.user_b:
            self.user_b_not_interested = True
            self.user_b_interested = False
            self.status = 'not_interested'
        self.save()


class MatchHistory(models.Model):
    """Track match history and prevent duplicate suggestions."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='match_history'
    )
    matched_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='matched_by_history'
    )
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name='history_records',
        null=True,
        blank=True
    )
    
    # Action tracking
    action = models.CharField(
        max_length=20,
        choices=[
            ('suggested', 'Suggested'),
            ('viewed', 'Viewed'),
            ('interested', 'Interested'),
            ('not_interested', 'Not Interested'),
            ('connected', 'Connected'),
        ]
    )
    
    # Notes
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'accounts'
        verbose_name = 'Match History'
        verbose_name_plural = 'Match Histories'
        unique_together = ['user', 'matched_user', 'action']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'action', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} - {self.action} - {self.matched_user.full_name}"
