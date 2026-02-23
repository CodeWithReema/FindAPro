"""
Admin interface for multi-mode profile system.
"""

from django.contrib import admin
from django.utils import timezone
from .modes_models import (
    Skill, FreelanceListing, FreelancePortfolioItem,
    SkillSwapListing, SkillSwapJob, SkillCredit
)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """Admin for Skill model."""
    
    list_display = ['name', 'category', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['category', 'name']


class FreelancePortfolioItemInline(admin.TabularInline):
    """Inline admin for portfolio items."""
    
    model = FreelancePortfolioItem
    extra = 1
    fields = ['item_type', 'title', 'image', 'url', 'order', 'is_featured']


@admin.register(FreelanceListing)
class FreelanceListingAdmin(admin.ModelAdmin):
    """Admin for FreelanceListing model."""
    
    list_display = [
        'user', 'title', 'pricing_type', 'availability_status',
        'is_active', 'is_featured', 'is_verified', 'created_at'
    ]
    list_filter = [
        'pricing_type', 'availability_status', 'is_active',
        'is_featured', 'is_verified', 'created_at'
    ]
    search_fields = ['user__username', 'user__email', 'title', 'bio']
    filter_horizontal = ['skills']
    inlines = [FreelancePortfolioItemInline]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Basic Information', {
            'fields': ('title', 'bio', 'headline')
        }),
        ('Skills & Expertise', {
            'fields': ('skills', 'expertise_tags')
        }),
        ('Pricing', {
            'fields': (
                'pricing_type', 'hourly_rate', 'project_rate_min',
                'project_rate_max', 'currency'
            )
        }),
        ('Portfolio Links', {
            'fields': ('portfolio_url', 'github_url', 'linkedin_url', 'behance_url')
        }),
        ('Availability', {
            'fields': ('availability_status', 'availability_notes', 'timezone')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured', 'is_verified')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(FreelancePortfolioItem)
class FreelancePortfolioItemAdmin(admin.ModelAdmin):
    """Admin for FreelancePortfolioItem model."""
    
    list_display = ['listing', 'item_type', 'title', 'order', 'is_featured', 'created_at']
    list_filter = ['item_type', 'is_featured', 'created_at']
    search_fields = ['title', 'description']
    ordering = ['-is_featured', 'order', '-created_at']


@admin.register(SkillSwapListing)
class SkillSwapListingAdmin(admin.ModelAdmin):
    """Admin for SkillSwapListing model."""
    
    list_display = [
        'user', 'credits_balance', 'is_active', 'is_verified', 'created_at'
    ]
    list_filter = ['is_active', 'is_verified', 'accepts_remote', 'created_at']
    search_fields = ['user__username', 'user__email', 'bio']
    filter_horizontal = ['skills_offered', 'skills_wanted']
    readonly_fields = ['credits_earned', 'credits_spent', 'created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Bio', {
            'fields': ('bio',)
        }),
        ('Skills Offered', {
            'fields': ('skills_offered', 'additional_skills_offered')
        }),
        ('Skills Wanted', {
            'fields': ('skills_wanted', 'additional_skills_wanted')
        }),
        ('Credits', {
            'fields': ('credits_earned', 'credits_spent'),
            'description': 'Credits are automatically updated when transactions are approved.'
        }),
        ('Location', {
            'fields': ('location_preference', 'accepts_remote')
        }),
        ('Status', {
            'fields': ('is_active', 'is_verified')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def credits_balance(self, obj):
        """Display credit balance."""
        return obj.credits_balance
    credits_balance.short_description = 'Credit Balance'


@admin.register(SkillSwapJob)
class SkillSwapJobAdmin(admin.ModelAdmin):
    """Admin for SkillSwapJob model."""
    
    list_display = [
        'title', 'requester', 'provider', 'skill_needed',
        'hours_required', 'status', 'credits_in_escrow', 'posted_at'
    ]
    list_filter = ['status', 'skill_needed', 'posted_at']
    search_fields = [
        'title', 'description',
        'requester__username', 'requester__email',
        'provider__username', 'provider__email'
    ]
    readonly_fields = [
        'posted_at', 'accepted_at', 'started_at',
        'completed_at', 'cancelled_at', 'dispute_resolved_at'
    ]
    
    fieldsets = (
        ('Job Details', {
            'fields': ('title', 'description', 'skill_needed', 'hours_required')
        }),
        ('Participants', {
            'fields': ('requester', 'provider')
        }),
        ('Status', {
            'fields': ('status', 'requester_confirmed', 'provider_confirmed')
        }),
        ('Escrow', {
            'fields': ('credits_in_escrow',)
        }),
        ('Dates', {
            'fields': (
                'posted_at', 'accepted_at', 'started_at',
                'completed_at', 'cancelled_at'
            ),
            'classes': ('collapse',)
        }),
        ('Dispute', {
            'fields': (
                'dispute_reason', 'dispute_resolved_by', 'dispute_resolved_at'
            ),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )
    
    actions = ['mark_completed', 'cancel_job', 'resolve_dispute']
    
    def mark_completed(self, request, queryset):
        """Mark selected jobs as completed."""
        from .credit_service import CreditTransactionService
        count = 0
        for job in queryset:
            if job.status in ['accepted', 'in_progress']:
                job.status = 'completed'
                job.completed_at = timezone.now()
                job.requester_confirmed = True
                job.provider_confirmed = True
                job.save()
                # Release escrow
                CreditTransactionService.release_escrow(job)
                count += 1
        self.message_user(request, f'{count} job(s) marked as completed.')
    mark_completed.short_description = 'Mark as completed and release escrow'
    
    def cancel_job(self, request, queryset):
        """Cancel selected jobs and refund escrow."""
        from .credit_service import CreditTransactionService
        count = 0
        for job in queryset:
            if job.status not in ['completed', 'cancelled']:
                CreditTransactionService.refund_escrow(job, reason="Cancelled by admin")
                count += 1
        self.message_user(request, f'{count} job(s) cancelled and escrow refunded.')
    cancel_job.short_description = 'Cancel jobs and refund escrow'
    
    def resolve_dispute(self, request, queryset):
        """Resolve disputes for selected jobs."""
        from django.utils import timezone
        count = queryset.filter(status='disputed').update(
            dispute_resolved_by=request.user,
            dispute_resolved_at=timezone.now(),
            status='completed'
        )
        self.message_user(request, f'{count} dispute(s) resolved.')
    resolve_dispute.short_description = 'Resolve disputes'


@admin.register(SkillCredit)
class SkillCreditAdmin(admin.ModelAdmin):
    """Admin for SkillCredit model."""
    
    list_display = [
        'from_user', 'to_user', 'transaction_type', 'credits',
        'skill_swapped', 'status', 'job', 'created_at'
    ]
    list_filter = ['transaction_type', 'status', 'created_at']
    search_fields = [
        'description', 'notes', 'admin_notes',
        'from_user__username', 'from_user__email',
        'to_user__username', 'to_user__email'
    ]
    readonly_fields = ['created_at', 'updated_at', 'verified_at']
    
    fieldsets = (
        ('Transaction', {
            'fields': ('from_user', 'to_user', 'transaction_type', 'credits', 'status')
        }),
        ('Details', {
            'fields': ('job', 'skill_swapped', 'description', 'swap_date')
        }),
        ('Verification', {
            'fields': ('verified_by', 'verified_at')
        }),
        ('Admin', {
            'fields': ('admin_notes', 'expires_at')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_transactions', 'reject_transactions', 'create_adjustment']
    
    def approve_transactions(self, request, queryset):
        """Approve selected transactions."""
        count = queryset.filter(status='pending').update(
            status='approved',
            verified_by=request.user,
            verified_at=timezone.now()
        )
        self.message_user(request, f'{count} transaction(s) approved.')
    approve_transactions.short_description = 'Approve selected transactions'
    
    def reject_transactions(self, request, queryset):
        """Reject selected transactions."""
        count = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f'{count} transaction(s) rejected.')
    reject_transactions.short_description = 'Reject selected transactions'
    
    def create_adjustment(self, request, queryset):
        """Create manual credit adjustment for selected users."""
        from .credit_service import CreditTransactionService
        count = 0
        for credit in queryset:
            if credit.to_user:
                CreditTransactionService.admin_adjustment(
                    user=credit.to_user,
                    credits=credit.credits,
                    description=f"Manual adjustment: {credit.description}",
                    admin_user=request.user,
                    notes=f"Created from transaction {credit.id}"
                )
                count += 1
        self.message_user(request, f'{count} adjustment(s) created.')
    create_adjustment.short_description = 'Create manual adjustments'
