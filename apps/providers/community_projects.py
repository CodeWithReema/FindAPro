"""
Community project board models for collaborative multi-person projects.
"""

from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal


class CommunityProject(models.Model):
    """Multi-person collaborative project."""
    
    PROJECT_TYPE_CHOICES = [
        ('community', 'Community Project'),
        ('creative', 'Creative Collaboration'),
        ('business', 'Business Venture'),
        ('learning', 'Learning Project'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('recruiting', 'Recruiting Team Members'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    COMPENSATION_TYPE_CHOICES = [
        ('paid', 'Paid'),
        ('credits', 'Credits'),
        ('volunteer', 'Volunteer'),
        ('mixed', 'Mixed'),
    ]
    
    # Creator
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_projects',
        help_text='User who created the project'
    )
    
    # Project Details
    title = models.CharField(max_length=200)
    description = models.TextField(help_text='Detailed project description')
    project_type = models.CharField(
        max_length=20,
        choices=PROJECT_TYPE_CHOICES,
        default='community'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    
    # Timeline
    start_date = models.DateField(null=True, blank=True, help_text='Project start date')
    end_date = models.DateField(null=True, blank=True, help_text='Expected completion date')
    timeline_description = models.CharField(
        max_length=255,
        blank=True,
        help_text='Timeline description (e.g., "3-6 months", "Ongoing")'
    )
    
    # Location
    location_city = models.CharField(max_length=100)
    location_state = models.CharField(max_length=50)
    location_address = models.CharField(max_length=255, blank=True)
    location_zip = models.CharField(max_length=20, blank=True)
    is_remote_friendly = models.BooleanField(
        default=False,
        help_text='Can team members work remotely?'
    )
    
    # Compensation
    compensation_type = models.CharField(
        max_length=20,
        choices=COMPENSATION_TYPE_CHOICES,
        default='volunteer'
    )
    budget_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Total project budget (if applicable)'
    )
    
    # Media
    featured_image = models.ImageField(
        upload_to='projects/featured/',
        null=True,
        blank=True,
        help_text='Main project image'
    )
    
    # Metadata
    is_featured = models.BooleanField(default=False, help_text='Featured community project')
    view_count = models.IntegerField(default=0)
    application_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Community Project'
        verbose_name_plural = 'Community Projects'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['project_type', 'status']),
            models.Index(fields=['location_city', 'location_state', '-created_at']),
            models.Index(fields=['is_featured', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_project_type_display()})"
    
    def get_absolute_url(self):
        return reverse('providers:project_detail', kwargs={'pk': self.pk})
    
    @property
    def total_roles(self):
        """Total number of roles needed."""
        return self.roles.count()
    
    @property
    def filled_roles(self):
        """Number of filled roles."""
        return self.roles.filter(status='filled').count()
    
    @property
    def open_roles(self):
        """Number of open roles."""
        return self.roles.filter(status='open').count()
    
    @property
    def is_recruiting(self):
        """Check if project is actively recruiting."""
        return self.status == 'recruiting' and self.open_roles > 0
    
    @property
    def team_members(self):
        """Get all team members."""
        return self.members.filter(status='active').select_related('user')


class ProjectRole(models.Model):
    """Role needed for a project."""
    
    STATUS_CHOICES = [
        ('open', 'Open - Accepting Applications'),
        ('filled', 'Filled'),
        ('closed', 'Closed - No Longer Needed'),
    ]
    
    COMPENSATION_TYPE_CHOICES = [
        ('paid', 'Paid'),
        ('credits', 'Credits'),
        ('volunteer', 'Volunteer'),
    ]
    
    project = models.ForeignKey(
        CommunityProject,
        on_delete=models.CASCADE,
        related_name='roles',
        help_text='Project this role belongs to'
    )
    
    # Role Details
    title = models.CharField(max_length=200, help_text='Role title (e.g., "Lead Electrician")')
    description = models.TextField(help_text='Role description and responsibilities')
    skill_required = models.ForeignKey(
        'accounts.Skill',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='project_roles',
        help_text='Primary skill required for this role'
    )
    skills_preferred = models.ManyToManyField(
        'accounts.Skill',
        blank=True,
        related_name='preferred_roles',
        help_text='Additional preferred skills'
    )
    
    # Requirements
    time_commitment_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Hours per week/month required',
        validators=[MinValueValidator(0)]
    )
    time_commitment_description = models.CharField(
        max_length=255,
        blank=True,
        help_text='Time commitment description (e.g., "10 hours/week", "Full-time")'
    )
    experience_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
            ('expert', 'Expert'),
        ],
        default='intermediate'
    )
    
    # Compensation
    compensation_type = models.CharField(
        max_length=20,
        choices=COMPENSATION_TYPE_CHOICES,
        default='volunteer'
    )
    compensation_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Compensation amount (pay rate, credits, etc.)'
    )
    compensation_description = models.CharField(
        max_length=255,
        blank=True,
        help_text='Compensation description'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open'
    )
    filled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='filled_roles',
        help_text='User who filled this role'
    )
    filled_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Project Role'
        verbose_name_plural = 'Project Roles'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.title} - {self.project.title}"
    
    @property
    def application_count(self):
        """Number of applications for this role."""
        return self.applications.filter(status='pending').count()


class ProjectApplication(models.Model):
    """Application for a project role."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    role = models.ForeignKey(
        ProjectRole,
        on_delete=models.CASCADE,
        related_name='applications',
        help_text='Role being applied for'
    )
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='project_applications',
        help_text='User applying for the role'
    )
    
    # Application Details
    cover_letter = models.TextField(help_text='Why you\'re interested and qualified')
    relevant_experience = models.TextField(
        blank=True,
        help_text='Relevant experience and portfolio links'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_applications',
        help_text='Project creator who reviewed this application'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True, help_text='Internal review notes')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Project Application'
        verbose_name_plural = 'Project Applications'
        ordering = ['-created_at']
        unique_together = ['role', 'applicant']
        indexes = [
            models.Index(fields=['role', 'status', '-created_at']),
            models.Index(fields=['applicant', 'status']),
        ]
    
    def __str__(self):
        return f"{self.applicant.full_name} - {self.role.title}"


class ProjectMember(models.Model):
    """Team member of a project."""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('removed', 'Removed'),
    ]
    
    project = models.ForeignKey(
        CommunityProject,
        on_delete=models.CASCADE,
        related_name='members',
        help_text='Project this member belongs to'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='project_memberships',
        help_text='Team member'
    )
    role = models.ForeignKey(
        ProjectRole,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members',
        help_text='Role this member fills'
    )
    
    # Member Details
    role_title = models.CharField(
        max_length=200,
        blank=True,
        help_text='Custom role title (if different from role.title)'
    )
    is_creator = models.BooleanField(default=False, help_text='Is this the project creator?')
    is_lead = models.BooleanField(default=False, help_text='Is this a project lead?')
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Project Member'
        verbose_name_plural = 'Project Members'
        unique_together = ['project', 'user']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['user', 'status']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} - {self.project.title}"


class ProjectMilestone(models.Model):
    """Project milestone/task."""
    
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('blocked', 'Blocked'),
    ]
    
    project = models.ForeignKey(
        CommunityProject,
        on_delete=models.CASCADE,
        related_name='milestones',
        help_text='Project this milestone belongs to'
    )
    
    # Milestone Details
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='not_started'
    )
    
    # Assignment
    assigned_to = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='assigned_milestones',
        help_text='Team members assigned to this milestone'
    )
    
    # Completion
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='completed_milestones',
        help_text='User who marked milestone as completed'
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Project Milestone'
        verbose_name_plural = 'Project Milestones'
        ordering = ['due_date', 'created_at']
    
    def __str__(self):
        return f"{self.title} - {self.project.title}"


class ProjectFile(models.Model):
    """File shared within a project."""
    
    FILE_TYPE_CHOICES = [
        ('document', 'Document'),
        ('image', 'Image'),
        ('design', 'Design File'),
        ('plan', 'Plan/Blueprint'),
        ('other', 'Other'),
    ]
    
    project = models.ForeignKey(
        CommunityProject,
        on_delete=models.CASCADE,
        related_name='files',
        help_text='Project this file belongs to'
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_project_files',
        help_text='User who uploaded the file'
    )
    
    # File Details
    file = models.FileField(upload_to='projects/files/')
    file_type = models.CharField(
        max_length=20,
        choices=FILE_TYPE_CHOICES,
        default='document'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Related items
    milestone = models.ForeignKey(
        ProjectMilestone,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='files',
        help_text='Related milestone (if applicable)'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Project File'
        verbose_name_plural = 'Project Files'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.project.title}"


class ProjectMessage(models.Model):
    """Message in project team discussion."""
    
    project = models.ForeignKey(
        CommunityProject,
        on_delete=models.CASCADE,
        related_name='messages',
        help_text='Project this message belongs to'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='project_messages_sent',
        help_text='User who sent the message'
    )
    
    # Message Details
    message = models.TextField()
    is_pinned = models.BooleanField(default=False, help_text='Pin important messages')
    
    # Related items
    milestone = models.ForeignKey(
        ProjectMilestone,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='messages',
        help_text='Related milestone (if applicable)'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Project Message'
        verbose_name_plural = 'Project Messages'
        ordering = ['-is_pinned', 'created_at']
        indexes = [
            models.Index(fields=['project', '-created_at']),
        ]
    
    def __str__(self):
        return f"Message from {self.sender.full_name} - {self.project.title}"
