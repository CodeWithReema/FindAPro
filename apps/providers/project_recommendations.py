"""
Recommendation service for matching users with projects.
"""

from django.db.models import Q, Count
from django.utils import timezone

from .community_projects import CommunityProject, ProjectRole, ProjectApplication
from apps.accounts.modes_models import Skill


class ProjectRecommendationService:
    """Service for recommending projects to users based on their skills."""
    
    @staticmethod
    def get_recommended_projects(user, limit=10):
        """
        Get recommended projects for a user based on their skills.
        
        Args:
            user: User instance
            limit: Maximum number of recommendations
        
        Returns:
            QuerySet of recommended projects
        """
        # Get user's skills
        user_skills = set()
        
        # From skill swap listing
        if hasattr(user, 'skill_swap_listing') and user.skill_swap_listing.is_active:
            user_skills.update(user.skill_swap_listing.skills_offered.all())
        
        # From freelance listing
        if hasattr(user, 'freelance_listing') and user.freelance_listing.is_active:
            user_skills.update(user.freelance_listing.skills.all())
        
        if not user_skills:
            # Return featured projects if user has no skills
            return CommunityProject.objects.filter(
                is_featured=True,
                status='recruiting'
            ).order_by('-created_at')[:limit]
        
        # Find projects with roles matching user's skills
        matching_roles = ProjectRole.objects.filter(
            project__status='recruiting',
            status='open',
            skill_required__in=user_skills
        ).select_related('project')
        
        # Get unique projects
        project_ids = matching_roles.values_list('project_id', flat=True).distinct()
        
        # Score projects based on skill matches
        projects = CommunityProject.objects.filter(
            id__in=project_ids
        ).annotate(
            matching_roles_count=Count(
                'roles',
                filter=Q(roles__skill_required__in=user_skills, roles__status='open')
            )
        ).order_by('-matching_roles_count', '-is_featured', '-created_at')
        
        return projects[:limit]
    
    @staticmethod
    def get_skill_match_score(user, project):
        """
        Calculate skill match score between user and project.
        
        Returns:
            float: Match score (0-100)
        """
        user_skills = set()
        
        if hasattr(user, 'skill_swap_listing') and user.skill_swap_listing.is_active:
            user_skills.update(user.skill_swap_listing.skills_offered.all())
        
        if hasattr(user, 'freelance_listing') and user.freelance_listing.is_active:
            user_skills.update(user.freelance_listing.skills.all())
        
        if not user_skills:
            return 0
        
        # Count matching roles
        matching_roles = project.roles.filter(
            status='open',
            skill_required__in=user_skills
        ).count()
        
        total_open_roles = project.open_roles
        
        if total_open_roles == 0:
            return 0
        
        # Calculate percentage
        match_percentage = (matching_roles / total_open_roles) * 100
        
        return match_percentage
