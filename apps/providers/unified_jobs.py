"""
Unified job/booking system for paid jobs, credit-based swaps, and barter proposals.
"""

from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal


class UnifiedJob(models.Model):
    """Unified job model supporting paid, credit-based, and barter proposals."""
    
    PAYMENT_TYPE_CHOICES = [
        ('paid', 'Paid Job'),
        ('credit', 'Credit-Based Swap'),
        ('barter', 'Barter Proposal'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('proposed', 'Proposal Sent'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('disputed', 'Disputed'),
    ]
    
    TIMELINE_CHOICES = [
        ('asap', 'As soon as possible'),
        ('this_week', 'This week'),
        ('next_week', 'Next week'),
        ('this_month', 'This month'),
        ('flexible', 'Flexible'),
    ]
    
    # Participants
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='jobs_requested',
        help_text='User requesting the service'
    )
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='jobs_provided',
        null=True,
        blank=True,
        help_text='User providing the service (set when accepted)'
    )
    
    # Job Type
    payment_type = models.CharField(
        max_length=20,
        choices=PAYMENT_TYPE_CHOICES,
        default='paid'
    )
    
    # Job Details
    title = models.CharField(max_length=200)
    description = models.TextField(help_text='Describe the work needed')
    timeline = models.CharField(
        max_length=20,
        choices=TIMELINE_CHOICES,
        default='flexible'
    )
    is_emergency = models.BooleanField(default=False)
    
    # Location
    service_address = models.CharField(max_length=255, blank=True)
    service_city = models.CharField(max_length=100, blank=True)
    service_state = models.CharField(max_length=50, blank=True)
    service_zip = models.CharField(max_length=20, blank=True)
    
    # Payment Type Specific Fields
    # For Paid Jobs
    budget_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text='Minimum budget (for paid jobs)'
    )
    budget_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text='Maximum budget (for paid jobs)'
    )
    agreed_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text='Agreed payment amount'
    )
    
    # For Credit-Based Jobs
    credits_requested = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.5)],
        help_text='Credits requested (hours)'
    )
    credits_agreed = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.5)],
        help_text='Agreed credits (hours)'
    )
    credits_in_escrow = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text='Credits held in escrow'
    )
    
    # For Barter Proposals
    barter_offer = models.TextField(
        blank=True,
        help_text='What you offer in exchange (for barter proposals)'
    )
    barter_request = models.TextField(
        blank=True,
        help_text='What you want in exchange (for barter proposals)'
    )
    
    # Related Models (for backward compatibility)
    related_quote_request = models.ForeignKey(
        'providers.QuoteRequest',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='unified_job',
        help_text='Related quote request (if converted from quote)'
    )
    related_skill_swap_job = models.ForeignKey(
        'accounts.SkillSwapJob',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='unified_jobs',
        help_text='Related skill swap job (if converted)'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Completion
    requester_confirmed = models.BooleanField(default=False)
    provider_confirmed = models.BooleanField(default=False)
    
    # Payment/Credit Processing
    payment_processed = models.BooleanField(default=False)
    payment_processed_at = models.DateTimeField(null=True, blank=True)
    
    # Contact Preferences
    preferred_contact = models.CharField(
        max_length=20,
        choices=[('email', 'Email'), ('phone', 'Phone'), ('either', 'Either')],
        default='either'
    )
    phone = models.CharField(max_length=20, blank=True)
    
    # Dispute
    dispute_reason = models.TextField(blank=True)
    dispute_resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='unified_job_disputes_resolved',
        help_text='Admin who resolved the dispute'
    )
    dispute_resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Unified Job'
        verbose_name_plural = 'Unified Jobs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['requester', 'status', '-created_at']),
            models.Index(fields=['provider', 'status', '-created_at']),
            models.Index(fields=['payment_type', 'status']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_payment_type_display()}) - {self.get_status_display()}"
    
    def get_absolute_url(self):
        return reverse('providers:unified_job_detail', kwargs={'pk': self.pk})
    
    @property
    def is_completed(self):
        """Check if job is completed and confirmed."""
        return (
            self.status == 'completed' and
            self.requester_confirmed and
            self.provider_confirmed
        )
    
    @property
    def has_pending_proposals(self):
        """Check if there are pending proposals."""
        return self.proposals.filter(status='pending').exists()
    
    def get_current_proposal(self):
        """Get the most recent accepted or pending proposal."""
        return self.proposals.filter(
            status__in=['accepted', 'pending']
        ).order_by('-created_at').first()


class JobProposal(models.Model):
    """Proposals and counter-offers for job negotiations."""
    
    PROPOSAL_TYPE_CHOICES = [
        ('initial', 'Initial Proposal'),
        ('counter', 'Counter Offer'),
        ('accept', 'Acceptance'),
        ('decline', 'Decline'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
    ]
    
    # Relationships
    job = models.ForeignKey(
        UnifiedJob,
        on_delete=models.CASCADE,
        related_name='proposals',
        help_text='Job this proposal is for'
    )
    proposed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_proposals',
        help_text='User making the proposal'
    )
    
    # Proposal Type
    proposal_type = models.CharField(
        max_length=20,
        choices=PROPOSAL_TYPE_CHOICES,
        default='initial'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Proposal Details
    message = models.TextField(help_text='Proposal message')
    
    # Terms (varies by payment type)
    # For Paid Jobs
    proposed_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text='Proposed payment amount'
    )
    
    # For Credit Jobs
    proposed_credits = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.5)],
        help_text='Proposed credits (hours)'
    )
    
    # For Barter
    proposed_barter_offer = models.TextField(
        blank=True,
        help_text='Proposed barter offer'
    )
    proposed_barter_request = models.TextField(
        blank=True,
        help_text='Proposed barter request'
    )
    
    # Response
    response_message = models.TextField(blank=True, help_text='Response to this proposal')
    responded_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text='Proposal expiration date')
    
    class Meta:
        verbose_name = 'Job Proposal'
        verbose_name_plural = 'Job Proposals'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['job', 'status', '-created_at']),
            models.Index(fields=['proposed_by', 'status']),
        ]
    
    def __str__(self):
        return f"{self.get_proposal_type_display()} for {self.job.title} - {self.get_status_display()}"
    
    @property
    def is_expired(self):
        """Check if proposal has expired."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class JobMessage(models.Model):
    """Unified messaging thread for job discussions."""
    
    job = models.ForeignKey(
        UnifiedJob,
        on_delete=models.CASCADE,
        related_name='messages',
        help_text='Job this message belongs to'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_messages_sent',
        help_text='User who sent the message'
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_messages_received',
        help_text='User who receives the message'
    )
    
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Related proposal (if message is about a proposal)
    related_proposal = models.ForeignKey(
        JobProposal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='messages',
        help_text='Related proposal (if applicable)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Job Message'
        verbose_name_plural = 'Job Messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['job', '-created_at']),
            models.Index(fields=['recipient', 'is_read', '-created_at']),
        ]
    
    def __str__(self):
        return f"Message from {self.sender.full_name} for {self.job.title}"
    
    def mark_as_read(self):
        """Mark message as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
