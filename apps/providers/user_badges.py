"""
User badge/achievement system for community projects.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class UserBadge(models.Model):
    """Badge/achievement that can be earned by users."""
    
    BADGE_TYPE_CHOICES = [
        ('community_builder', 'Community Builder'),
        ('collaborator', 'Collaborator'),
        ('project_leader', 'Project Leader'),
        ('skill_sharer', 'Skill Sharer'),
        ('mentor', 'Mentor'),
        ('volunteer', 'Volunteer'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    badge_type = models.CharField(
        max_length=20,
        choices=BADGE_TYPE_CHOICES,
        help_text='Category of badge'
    )
    description = models.TextField(help_text='What this badge represents')
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text='Icon class or emoji (e.g., 🏆, fa-trophy)'
    )
    image = models.ImageField(
        upload_to='badges/',
        null=True,
        blank=True,
        help_text='Badge image'
    )
    criteria = models.TextField(
        help_text='How to earn this badge (e.g., "Complete 5 community projects")'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'User Badge'
        verbose_name_plural = 'User Badges'
        ordering = ['badge_type', 'name']
    
    def __str__(self):
        return self.name


class UserBadgeAward(models.Model):
    """Awarded badge to a user."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='badges_awarded',
        help_text='User who earned the badge'
    )
    badge = models.ForeignKey(
        UserBadge,
        on_delete=models.CASCADE,
        related_name='awards',
        help_text='Badge that was awarded'
    )
    awarded_at = models.DateTimeField(auto_now_add=True)
    awarded_for_project = models.ForeignKey(
        'providers.CommunityProject',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='badge_awards',
        help_text='Project that triggered this badge (if applicable)'
    )
    notes = models.TextField(blank=True, help_text='Additional notes about the award')
    
    class Meta:
        verbose_name = 'Badge Award'
        verbose_name_plural = 'Badge Awards'
        ordering = ['-awarded_at']
        unique_together = ['user', 'badge']
        indexes = [
            models.Index(fields=['user', '-awarded_at']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} - {self.badge.name}"


class BadgeAwardService:
    """Service for awarding badges based on user activity."""
    
    @staticmethod
    def check_and_award_badges(user):
        """Check if user qualifies for any badges and award them."""
        from .community_projects import CommunityProject, ProjectMember
        
        awards = []
        
        # Community Builder: Created 3+ projects
        created_count = CommunityProject.objects.filter(creator=user).count()
        if created_count >= 3:
            badge, _ = UserBadge.objects.get_or_create(
                slug='community_builder',
                defaults={
                    'name': 'Community Builder',
                    'badge_type': 'community_builder',
                    'description': 'Created 3 or more community projects',
                    'icon': '🏗️',
                    'criteria': 'Create 3 community projects',
                }
            )
            award, created = UserBadgeAward.objects.get_or_create(
                user=user,
                badge=badge
            )
            if created:
                awards.append(award)
        
        # Collaborator: Participated in 5+ projects
        participated_count = ProjectMember.objects.filter(
            user=user,
            status='active',
            is_creator=False
        ).count()
        if participated_count >= 5:
            badge, _ = UserBadge.objects.get_or_create(
                slug='collaborator',
                defaults={
                    'name': 'Collaborator',
                    'badge_type': 'collaborator',
                    'description': 'Participated in 5 or more projects',
                    'icon': '🤝',
                    'criteria': 'Join 5 projects as a team member',
                }
            )
            award, created = UserBadgeAward.objects.get_or_create(
                user=user,
                badge=badge
            )
            if created:
                awards.append(award)
        
        # Project Leader: Led 2+ completed projects
        led_count = CommunityProject.objects.filter(
            creator=user,
            status='completed'
        ).count()
        if led_count >= 2:
            badge, _ = UserBadge.objects.get_or_create(
                slug='project_leader',
                defaults={
                    'name': 'Project Leader',
                    'badge_type': 'project_leader',
                    'description': 'Successfully led 2 or more projects to completion',
                    'icon': '👑',
                    'criteria': 'Complete 2 projects as creator',
                }
            )
            award, created = UserBadgeAward.objects.get_or_create(
                user=user,
                badge=badge
            )
            if created:
                awards.append(award)
        
        # Volunteer: Participated in 3+ volunteer projects
        volunteer_count = ProjectMember.objects.filter(
            user=user,
            status='active',
            project__compensation_type='volunteer'
        ).count()
        if volunteer_count >= 3:
            badge, _ = UserBadge.objects.get_or_create(
                slug='volunteer',
                defaults={
                    'name': 'Volunteer',
                    'badge_type': 'volunteer',
                    'description': 'Participated in 3 or more volunteer projects',
                    'icon': '❤️',
                    'criteria': 'Join 3 volunteer projects',
                }
            )
            award, created = UserBadgeAward.objects.get_or_create(
                user=user,
                badge=badge
            )
            if created:
                awards.append(award)
        
        return awards
