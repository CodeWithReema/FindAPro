"""
Admin configuration for providers app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import ServiceCategory, ServiceProvider, FavoriteProvider, ProviderImage, QuoteRequest
from .unified_jobs import UnifiedJob, JobProposal, JobMessage
from .skill_analytics import SkillDemand, SkillSupply, SkillMarketOpportunity
from .community_projects import (
    CommunityProject, ProjectRole, ProjectApplication,
    ProjectMember, ProjectMilestone, ProjectFile, ProjectMessage
)
from .user_badges import UserBadge, UserBadgeAward


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    """Admin for ServiceCategory model."""
    
    list_display = ['name', 'slug', 'icon', 'provider_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']


class ProviderImageInline(admin.TabularInline):
    """Inline admin for provider gallery images."""
    model = ProviderImage
    extra = 1
    fields = ['image', 'caption', 'is_featured', 'order']


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    """Admin for ServiceProvider model."""
    
    list_display = [
        'name', 'category', 'city', 'state', 'pricing_range',
        'is_verified_badge', 'is_available_now', 'accepts_emergency', 'is_active', 'average_rating', 'review_count', 'created_at'
    ]
    list_filter = ['category', 'is_verified', 'is_active', 'is_featured', 'is_available_now', 'accepts_emergency', 'pricing_range', 'state']
    search_fields = ['name', 'description', 'skills', 'email', 'city']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['-created_at']
    readonly_fields = ['average_rating', 'review_count', 'created_at', 'updated_at']
    inlines = [ProviderImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'slug', 'tagline', 'description')
        }),
        ('Category & Skills', {
            'fields': ('category', 'skills')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'website')
        }),
        ('Location', {
            'fields': ('address', 'city', 'state', 'zip_code')
        }),
        ('Business Details', {
            'fields': ('pricing_range', 'years_experience')
        }),
        ('Media', {
            'fields': ('image', 'logo')
        }),
        ('Status', {
            'fields': ('is_verified', 'is_active', 'is_featured')
        }),
        ('Emergency & Availability', {
            'fields': ('is_available_now', 'accepts_emergency', 'emergency_rate_info')
        }),
        ('Job Acceptance Preferences', {
            'fields': ('accepts_paid_jobs', 'accepts_credit_jobs', 'accepts_barter')
        }),
        ('Statistics (Read Only)', {
            'fields': ('average_rating', 'review_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_verified_badge(self, obj):
        if obj.is_verified:
            return format_html('<span style="color: green;">✓ Verified</span>')
        return format_html('<span style="color: gray;">—</span>')
    is_verified_badge.short_description = 'Verified'


@admin.register(ProviderImage)
class ProviderImageAdmin(admin.ModelAdmin):
    """Admin for ProviderImage model."""
    
    list_display = ['provider', 'caption', 'is_featured', 'order', 'created_at']
    list_filter = ['is_featured', 'created_at']
    search_fields = ['provider__name', 'caption']
    ordering = ['provider', '-is_featured', 'order']
    raw_id_fields = ['provider']


@admin.register(FavoriteProvider)
class FavoriteProviderAdmin(admin.ModelAdmin):
    """Admin for FavoriteProvider model."""
    
    list_display = ['user', 'provider', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email', 'provider__name']
    ordering = ['-created_at']
    raw_id_fields = ['user', 'provider']


@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    """Admin for QuoteRequest model."""
    
    list_display = ['title', 'user', 'provider', 'status', 'budget', 'quote_amount', 'created_at']
    list_filter = ['status', 'timeline', 'budget', 'created_at']
    search_fields = ['title', 'description', 'user__username', 'user__email', 'provider__name']
    ordering = ['-created_at']
    raw_id_fields = ['user', 'provider']
    readonly_fields = ['created_at', 'updated_at', 'quoted_at']
    
    fieldsets = (
        ('Request Info', {
            'fields': ('user', 'provider', 'title', 'description', 'status')
        }),
        ('Project Details', {
            'fields': ('timeline', 'budget', 'preferred_contact', 'phone')
        }),
        ('Service Location', {
            'fields': ('service_address', 'service_city', 'service_zip')
        }),
        ('Quote Response', {
            'fields': ('quote_amount', 'quote_message', 'quoted_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class JobProposalInline(admin.TabularInline):
    """Inline admin for job proposals."""
    model = JobProposal
    extra = 0
    readonly_fields = ['created_at', 'responded_at']
    fields = ['proposal_type', 'status', 'message', 'proposed_amount', 'proposed_credits', 'created_at']


class JobMessageInline(admin.TabularInline):
    """Inline admin for job messages."""
    model = JobMessage
    extra = 0
    readonly_fields = ['created_at', 'read_at']
    fields = ['sender', 'recipient', 'message', 'is_read', 'created_at']


@admin.register(UnifiedJob)
class UnifiedJobAdmin(admin.ModelAdmin):
    """Admin for UnifiedJob model."""
    
    list_display = [
        'title', 'requester', 'provider', 'payment_type',
        'status', 'agreed_amount', 'credits_agreed', 'created_at'
    ]
    list_filter = ['payment_type', 'status', 'is_emergency', 'created_at']
    search_fields = [
        'title', 'description',
        'requester__username', 'requester__email',
        'provider__username', 'provider__email'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'accepted_at',
        'started_at', 'completed_at', 'cancelled_at',
        'payment_processed_at', 'dispute_resolved_at'
    ]
    raw_id_fields = ['requester', 'provider', 'related_quote_request', 'related_skill_swap_job']
    inlines = [JobProposalInline, JobMessageInline]
    
    fieldsets = (
        ('Job Details', {
            'fields': ('payment_type', 'title', 'description', 'timeline', 'is_emergency')
        }),
        ('Participants', {
            'fields': ('requester', 'provider')
        }),
        ('Paid Job Fields', {
            'fields': ('budget_min', 'budget_max', 'agreed_amount'),
            'classes': ('collapse',)
        }),
        ('Credit Job Fields', {
            'fields': ('credits_requested', 'credits_agreed', 'credits_in_escrow'),
            'classes': ('collapse',)
        }),
        ('Barter Fields', {
            'fields': ('barter_offer', 'barter_request'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status', 'requester_confirmed', 'provider_confirmed', 'payment_processed')
        }),
        ('Location', {
            'fields': ('service_address', 'service_city', 'service_state', 'service_zip')
        }),
        ('Contact', {
            'fields': ('preferred_contact', 'phone')
        }),
        ('Related Jobs', {
            'fields': ('related_quote_request', 'related_skill_swap_job'),
            'classes': ('collapse',)
        }),
        ('Dispute', {
            'fields': ('dispute_reason', 'dispute_resolved_by', 'dispute_resolved_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'updated_at', 'accepted_at',
                'started_at', 'completed_at', 'cancelled_at',
                'payment_processed_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_completed', 'cancel_job', 'process_payment']
    
    def mark_completed(self, request, queryset):
        """Mark selected jobs as completed."""
        count = 0
        for job in queryset.filter(status__in=['accepted', 'in_progress']):
            job.status = 'completed'
            job.completed_at = timezone.now()
            job.requester_confirmed = True
            job.provider_confirmed = True
            job.save()
            count += 1
        self.message_user(request, f'{count} job(s) marked as completed.')
    mark_completed.short_description = 'Mark as completed'
    
    def cancel_job(self, request, queryset):
        """Cancel selected jobs."""
        count = queryset.filter(status__in=['pending', 'proposed', 'accepted', 'in_progress']).update(
            status='cancelled',
            cancelled_at=timezone.now()
        )
        self.message_user(request, f'{count} job(s) cancelled.')
    cancel_job.short_description = 'Cancel jobs'
    
    def process_payment(self, request, queryset):
        """Mark payment as processed."""
        count = queryset.filter(
            status='completed',
            payment_processed=False
        ).update(
            payment_processed=True,
            payment_processed_at=timezone.now()
        )
        self.message_user(request, f'{count} payment(s) marked as processed.')
    process_payment.short_description = 'Mark payment as processed'


@admin.register(JobProposal)
class JobProposalAdmin(admin.ModelAdmin):
    """Admin for JobProposal model."""
    
    list_display = [
        'job', 'proposed_by', 'proposal_type', 'status',
        'proposed_amount', 'proposed_credits', 'created_at'
    ]
    list_filter = ['proposal_type', 'status', 'created_at']
    search_fields = [
        'message', 'job__title',
        'proposed_by__username', 'proposed_by__email'
    ]
    readonly_fields = ['created_at', 'updated_at', 'responded_at']
    raw_id_fields = ['job', 'proposed_by']
    
    fieldsets = (
        ('Proposal', {
            'fields': ('job', 'proposed_by', 'proposal_type', 'status', 'message')
        }),
        ('Terms', {
            'fields': ('proposed_amount', 'proposed_credits', 'proposed_barter_offer', 'proposed_barter_request')
        }),
        ('Response', {
            'fields': ('response_message', 'responded_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'expires_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(JobMessage)
class JobMessageAdmin(admin.ModelAdmin):
    """Admin for JobMessage model."""
    
    list_display = ['job', 'sender', 'recipient', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['message', 'job__title', 'sender__username', 'recipient__username']
    readonly_fields = ['created_at', 'read_at']
    raw_id_fields = ['job', 'sender', 'recipient', 'related_proposal']
    
    fieldsets = (
        ('Message', {
            'fields': ('job', 'sender', 'recipient', 'message', 'related_proposal')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(SkillDemand)
class SkillDemandAdmin(admin.ModelAdmin):
    """Admin for SkillDemand model."""
    
    list_display = ['skill', 'city', 'state', 'demand_score', 'demand_change_percent', 'calculated_at']
    list_filter = ['city', 'state', 'calculated_at']
    search_fields = ['skill__name', 'city', 'state']
    readonly_fields = ['calculated_at']
    raw_id_fields = ['skill']
    
    fieldsets = (
        ('Skill & Location', {
            'fields': ('skill', 'city', 'state', 'zip_code', 'radius_miles')
        }),
        ('Demand Metrics', {
            'fields': ('demand_score', 'job_requests_count', 'skill_swap_wants_count', 'total_demand_signals')
        }),
        ('Trend Analysis', {
            'fields': ('previous_demand_score', 'demand_change_percent')
        }),
        ('Time Period', {
            'fields': ('period_start', 'period_end', 'calculated_at')
        }),
    )


@admin.register(SkillSupply)
class SkillSupplyAdmin(admin.ModelAdmin):
    """Admin for SkillSupply model."""
    
    list_display = ['skill', 'city', 'state', 'supply_score', 'supply_change_percent', 'calculated_at']
    list_filter = ['city', 'state', 'calculated_at']
    search_fields = ['skill__name', 'city', 'state']
    readonly_fields = ['calculated_at']
    raw_id_fields = ['skill']
    
    fieldsets = (
        ('Skill & Location', {
            'fields': ('skill', 'city', 'state', 'zip_code', 'radius_miles')
        }),
        ('Supply Metrics', {
            'fields': ('supply_score', 'provider_count', 'skill_swap_offers_count', 'freelance_listings_count', 'total_supply_signals')
        }),
        ('Trend Analysis', {
            'fields': ('previous_supply_score', 'supply_change_percent')
        }),
        ('Time Period', {
            'fields': ('period_start', 'period_end', 'calculated_at')
        }),
    )


@admin.register(SkillMarketOpportunity)
class SkillMarketOpportunityAdmin(admin.ModelAdmin):
    """Admin for SkillMarketOpportunity model."""
    
    list_display = ['skill', 'city', 'state', 'opportunity_score', 'market_status', 'calculated_at']
    list_filter = ['market_status', 'city', 'state', 'calculated_at']
    search_fields = ['skill__name', 'city', 'state']
    readonly_fields = ['calculated_at']
    raw_id_fields = ['skill']
    
    fieldsets = (
        ('Skill & Location', {
            'fields': ('skill', 'city', 'state', 'zip_code')
        }),
        ('Market Metrics', {
            'fields': ('demand_score', 'supply_score', 'opportunity_score', 'market_status')
        }),
        ('Time Period', {
            'fields': ('period_start', 'period_end', 'calculated_at')
        }),
    )


class ProjectRoleInline(admin.TabularInline):
    """Inline admin for project roles."""
    model = ProjectRole
    extra = 1
    fields = ['title', 'skill_required', 'status', 'compensation_type']


class ProjectMemberInline(admin.TabularInline):
    """Inline admin for project members."""
    model = ProjectMember
    extra = 0
    fields = ['user', 'role', 'role_title', 'is_lead', 'status']
    raw_id_fields = ['user', 'role']


@admin.register(CommunityProject)
class CommunityProjectAdmin(admin.ModelAdmin):
    """Admin for CommunityProject model."""
    
    list_display = ['title', 'creator', 'project_type', 'status', 'location_city', 'open_roles', 'filled_roles', 'created_at']
    list_filter = ['project_type', 'status', 'compensation_type', 'is_featured', 'created_at']
    search_fields = ['title', 'description', 'creator__username', 'creator__email', 'location_city']
    readonly_fields = ['created_at', 'updated_at', 'published_at', 'started_at', 'completed_at', 'view_count', 'application_count']
    raw_id_fields = ['creator']
    inlines = [ProjectRoleInline, ProjectMemberInline]
    
    fieldsets = (
        ('Project Details', {
            'fields': ('creator', 'title', 'description', 'project_type', 'status', 'featured_image')
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date', 'timeline_description')
        }),
        ('Location', {
            'fields': ('location_city', 'location_state', 'location_address', 'location_zip', 'is_remote_friendly')
        }),
        ('Compensation', {
            'fields': ('compensation_type', 'budget_total')
        }),
        ('Metadata', {
            'fields': ('is_featured', 'view_count', 'application_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at', 'started_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_featured', 'mark_completed', 'publish_projects']
    
    def mark_featured(self, request, queryset):
        """Mark selected projects as featured."""
        count = queryset.update(is_featured=True)
        self.message_user(request, f'{count} project(s) marked as featured.')
    mark_featured.short_description = 'Mark as featured'
    
    def mark_completed(self, request, queryset):
        """Mark selected projects as completed."""
        from django.utils import timezone
        count = queryset.filter(status__in=['recruiting', 'in_progress']).update(
            status='completed',
            completed_at=timezone.now()
        )
        self.message_user(request, f'{count} project(s) marked as completed.')
    mark_completed.short_description = 'Mark as completed'
    
    def publish_projects(self, request, queryset):
        """Publish draft projects."""
        from django.utils import timezone
        count = queryset.filter(status='draft').update(
            status='recruiting',
            published_at=timezone.now()
        )
        self.message_user(request, f'{count} project(s) published.')
    publish_projects.short_description = 'Publish projects'


@admin.register(ProjectRole)
class ProjectRoleAdmin(admin.ModelAdmin):
    """Admin for ProjectRole model."""
    
    list_display = ['title', 'project', 'skill_required', 'status', 'compensation_type', 'created_at']
    list_filter = ['status', 'compensation_type', 'experience_level', 'created_at']
    search_fields = ['title', 'description', 'project__title']
    raw_id_fields = ['project', 'skill_required', 'filled_by']
    filter_horizontal = ['skills_preferred']
    
    fieldsets = (
        ('Role Details', {
            'fields': ('project', 'title', 'description', 'skill_required', 'skills_preferred')
        }),
        ('Requirements', {
            'fields': ('time_commitment_hours', 'time_commitment_description', 'experience_level')
        }),
        ('Compensation', {
            'fields': ('compensation_type', 'compensation_amount', 'compensation_description')
        }),
        ('Status', {
            'fields': ('status', 'filled_by', 'filled_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProjectApplication)
class ProjectApplicationAdmin(admin.ModelAdmin):
    """Admin for ProjectApplication model."""
    
    list_display = ['applicant', 'role', 'status', 'created_at', 'reviewed_at']
    list_filter = ['status', 'created_at', 'reviewed_at']
    search_fields = ['applicant__username', 'applicant__email', 'role__title', 'cover_letter']
    readonly_fields = ['created_at', 'updated_at', 'reviewed_at']
    raw_id_fields = ['role', 'applicant', 'reviewed_by']
    
    fieldsets = (
        ('Application', {
            'fields': ('role', 'applicant', 'cover_letter', 'relevant_experience', 'status')
        }),
        ('Review', {
            'fields': ('reviewed_by', 'reviewed_at', 'review_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    """Admin for ProjectMember model."""
    
    list_display = ['user', 'project', 'role_title', 'is_creator', 'is_lead', 'status', 'joined_at']
    list_filter = ['status', 'is_creator', 'is_lead', 'joined_at']
    search_fields = ['user__username', 'user__email', 'project__title']
    raw_id_fields = ['project', 'user', 'role']


@admin.register(ProjectMilestone)
class ProjectMilestoneAdmin(admin.ModelAdmin):
    """Admin for ProjectMilestone model."""
    
    list_display = ['title', 'project', 'status', 'due_date', 'completed_at']
    list_filter = ['status', 'created_at', 'due_date']
    search_fields = ['title', 'description', 'project__title']
    raw_id_fields = ['project', 'completed_by']
    filter_horizontal = ['assigned_to']


@admin.register(ProjectFile)
class ProjectFileAdmin(admin.ModelAdmin):
    """Admin for ProjectFile model."""
    
    list_display = ['title', 'project', 'file_type', 'uploaded_by', 'created_at']
    list_filter = ['file_type', 'created_at']
    search_fields = ['title', 'description', 'project__title']
    raw_id_fields = ['project', 'uploaded_by', 'milestone']


@admin.register(ProjectMessage)
class ProjectMessageAdmin(admin.ModelAdmin):
    """Admin for ProjectMessage model."""
    
    list_display = ['project', 'sender', 'is_pinned', 'created_at']
    list_filter = ['is_pinned', 'created_at']
    search_fields = ['message', 'project__title', 'sender__username']
    raw_id_fields = ['project', 'sender', 'milestone']


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    """Admin for UserBadge model."""
    
    list_display = ['name', 'badge_type', 'icon', 'is_active', 'created_at']
    list_filter = ['badge_type', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'criteria']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(UserBadgeAward)
class UserBadgeAwardAdmin(admin.ModelAdmin):
    """Admin for UserBadgeAward model."""
    
    list_display = ['user', 'badge', 'awarded_at', 'awarded_for_project']
    list_filter = ['badge', 'awarded_at']
    search_fields = ['user__username', 'user__email', 'badge__name']
    readonly_fields = ['awarded_at']
    raw_id_fields = ['user', 'badge', 'awarded_for_project']

