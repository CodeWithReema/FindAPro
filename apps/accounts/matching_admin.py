"""
Admin interface for matching system.
"""

from django.contrib import admin
from .matching_models import Match, MatchHistory


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    """Admin for Match model."""
    
    list_display = [
        'user_a', 'user_b', 'match_type', 'compatibility_score',
        'status', 'user_a_interested', 'user_b_interested', 'created_at'
    ]
    list_filter = [
        'match_type', 'status', 'user_a_interested', 'user_b_interested', 'created_at'
    ]
    search_fields = [
        'user_a__username', 'user_a__email', 'user_a__first_name', 'user_a__last_name',
        'user_b__username', 'user_b__email', 'user_b__first_name', 'user_b__last_name',
        'matching_skills'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'connected_at',
        'last_viewed_a', 'last_viewed_b'
    ]
    
    fieldsets = (
        ('Users', {
            'fields': ('user_a', 'user_b', 'match_type')
        }),
        ('Compatibility Scores', {
            'fields': (
                'compatibility_score',
                'skill_overlap_percentage',
                'geographic_proximity_score',
                'reputation_score',
                'availability_score',
                'matching_skills'
            )
        }),
        ('Status', {
            'fields': (
                'status',
                'user_a_interested', 'user_b_interested',
                'user_a_not_interested', 'user_b_not_interested'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'updated_at', 'connected_at',
                'last_viewed_a', 'last_viewed_b'
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_connected', 'reset_status']
    
    def mark_as_connected(self, request, queryset):
        """Mark selected matches as connected."""
        from django.utils import timezone
        count = queryset.update(status='connected', connected_at=timezone.now())
        self.message_user(request, f'{count} match(es) marked as connected.')
    mark_as_connected.short_description = 'Mark as connected'
    
    def reset_status(self, request, queryset):
        """Reset status to pending."""
        count = queryset.update(status='pending')
        self.message_user(request, f'{count} match(es) reset to pending.')
    reset_status.short_description = 'Reset to pending'


@admin.register(MatchHistory)
class MatchHistoryAdmin(admin.ModelAdmin):
    """Admin for MatchHistory model."""
    
    list_display = ['user', 'matched_user', 'action', 'match', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = [
        'user__username', 'user__email',
        'matched_user__username', 'matched_user__email',
        'notes'
    ]
    readonly_fields = ['created_at']
    ordering = ['-created_at']
