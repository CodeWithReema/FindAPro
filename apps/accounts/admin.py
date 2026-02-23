"""
Admin configuration for accounts app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser

# Import modes admin to register models
from . import modes_admin
# Import matching admin to register models
from . import matching_admin


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Custom admin for CustomUser model."""
    
    list_display = [
        'username', 'email', 'first_name', 'last_name', 'user_type',
        'is_freelancer_active', 'is_skill_swap_active', 'is_active', 'created_at'
    ]
    list_filter = [
        'user_type', 'is_freelancer_active', 'is_skill_swap_active',
        'is_active', 'is_staff', 'created_at'
    ]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'phone', 'avatar', 'bio', 'city', 'state', 'zip_code')
        }),
        ('Profile Modes', {
            'fields': (
                'is_freelancer_active', 'is_skill_swap_active', 'active_mode'
            ),
            'description': 'Multi-mode profile activation flags'
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('email', 'user_type', 'first_name', 'last_name')
        }),
    )

