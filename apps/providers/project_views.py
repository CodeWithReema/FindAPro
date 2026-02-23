"""
Views for community project board.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.db.models import Q, Count
from django.utils import timezone
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .community_projects import (
    CommunityProject, ProjectRole, ProjectApplication,
    ProjectMember, ProjectMilestone, ProjectFile, ProjectMessage
)
from .project_forms import (
    CommunityProjectForm, ProjectRoleFormSet, ProjectApplicationForm,
    ProjectMilestoneForm, ProjectMessageForm
)
from .project_recommendations import ProjectRecommendationService
from .user_badges import BadgeAwardService


class ProjectListView(ListView):
    """Browse all community projects."""
    
    model = CommunityProject
    template_name = 'providers/projects/list.html'
    context_object_name = 'projects'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = CommunityProject.objects.filter(
            status__in=['recruiting', 'in_progress']
        ).select_related('creator').prefetch_related('roles', 'members')
        
        # Filter by project type
        project_type = self.request.GET.get('type', '')
        if project_type:
            queryset = queryset.filter(project_type=project_type)
        
        # Filter by compensation type
        compensation = self.request.GET.get('compensation', '')
        if compensation:
            queryset = queryset.filter(compensation_type=compensation)
        
        # Filter by location
        city = self.request.GET.get('city', '')
        if city:
            queryset = queryset.filter(location_city__icontains=city)
        
        state = self.request.GET.get('state', '')
        if state:
            queryset = queryset.filter(location_state__icontains=state)
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        # Search
        search = self.request.GET.get('q', '')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Sort
        sort = self.request.GET.get('sort', 'newest')
        if sort == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort == 'oldest':
            queryset = queryset.order_by('created_at')
        elif sort == 'most_applications':
            queryset = queryset.annotate(
                app_count=Count('roles__applications')
            ).order_by('-app_count')
        elif sort == 'deadline':
            queryset = queryset.order_by('end_date')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project_types'] = CommunityProject.PROJECT_TYPE_CHOICES
        context['compensation_types'] = CommunityProject.COMPENSATION_TYPE_CHOICES
        
        # Get recommendations for logged-in users
        if self.request.user.is_authenticated:
            context['recommended_projects'] = ProjectRecommendationService.get_recommended_projects(
                self.request.user,
                limit=5
            )
        
        return context


class ProjectDetailView(DetailView):
    """View project details."""
    
    model = CommunityProject
    template_name = 'providers/projects/detail.html'
    context_object_name = 'project'
    
    def get_queryset(self):
        return CommunityProject.objects.select_related('creator').prefetch_related(
            'roles', 'roles__applications', 'members__user', 'milestones', 'files', 'messages'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object
        
        # Check if user is team member
        context['is_member'] = False
        context['is_creator'] = False
        if self.request.user.is_authenticated:
            member = project.members.filter(user=self.request.user).first()
            if member:
                context['is_member'] = True
                context['member'] = member
                context['is_creator'] = member.is_creator
        
        # Get user's applications
        context['user_applications'] = []
        if self.request.user.is_authenticated:
            context['user_applications'] = ProjectApplication.objects.filter(
                applicant=self.request.user,
                role__project=project
            )
        
        # Get open roles
        context['open_roles'] = project.roles.filter(status='open').select_related('skill_required')
        
        # Application form (if user is not already a member)
        if self.request.user.is_authenticated and not context['is_member']:
            context['application_form'] = ProjectApplicationForm()
        
        # Get user's existing applications
        if self.request.user.is_authenticated:
            context['user_applications'] = ProjectApplication.objects.filter(
                applicant=self.request.user,
                role__project=project
            ).select_related('role')
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle application submission."""
        self.object = self.get_object()
        project = self.object
        
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to apply.')
            return redirect('accounts:login')
        
        # Check if already a member
        if project.members.filter(user=request.user).exists():
            messages.info(request, 'You are already a team member.')
            return redirect('providers:project_detail', pk=project.pk)
        
        # Get role ID from form
        role_id = request.POST.get('role_id')
        if not role_id:
            messages.error(request, 'Please select a role to apply for.')
            return redirect('providers:project_detail', pk=project.pk)
        
        role = get_object_or_404(ProjectRole, pk=role_id, project=project, status='open')
        
        # Check if already applied
        existing_app = ProjectApplication.objects.filter(role=role, applicant=request.user).first()
        if existing_app:
            if existing_app.status == 'pending':
                messages.info(request, 'You have already applied for this role.')
            elif existing_app.status == 'accepted':
                messages.info(request, 'Your application has already been accepted!')
            elif existing_app.status == 'declined':
                messages.info(request, 'Your application was declined.')
            return redirect('providers:project_detail', pk=project.pk)
        
        # Create application
        form = ProjectApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.role = role
            application.applicant = request.user
            application.save()
            
            project.application_count += 1
            project.save()
            
            messages.success(request, 'Your application has been submitted!')
        else:
            messages.error(request, 'Please correct the errors below.')
        
        return redirect('providers:project_detail', pk=project.pk)


class ProjectCreateView(LoginRequiredMixin, CreateView):
    """Create a new community project."""
    
    model = CommunityProject
    form_class = CommunityProjectForm
    template_name = 'providers/projects/create.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['role_formset'] = ProjectRoleFormSet(self.request.POST)
        else:
            context['role_formset'] = ProjectRoleFormSet()
        return context
    
    def form_valid(self, form):
        form.instance.creator = self.request.user
        form.instance.status = 'draft'
        
        context = self.get_context_data()
        role_formset = context['role_formset']
        
        if role_formset.is_valid():
            project = form.save()
            
            # Save roles
            for role_form in role_formset:
                if role_form.cleaned_data and not role_form.cleaned_data.get('DELETE'):
                    role = role_form.save(commit=False)
                    role.project = project
                    role.save()
                    role_form.save_m2m()
            
            # Create project member for creator
            ProjectMember.objects.create(
                project=project,
                user=self.request.user,
                is_creator=True,
                is_lead=True,
                role_title='Project Creator'
            )
            
            # Check for badge awards
            BadgeAwardService.check_and_award_badges(self.request.user)
            
            messages.success(self.request, 'Project created! Add more details and publish when ready.')
            return redirect('providers:project_manage', pk=project.pk)
        
        return self.form_invalid(form)


class ProjectManageView(LoginRequiredMixin, DetailView):
    """Project management dashboard."""
    
    model = CommunityProject
    template_name = 'providers/projects/manage.html'
    context_object_name = 'project'
    
    def get_queryset(self):
        return CommunityProject.objects.select_related('creator').prefetch_related(
            'roles', 'roles__applications__applicant',
            'members__user', 'milestones', 'files', 'messages__sender'
        )
    
    def dispatch(self, request, *args, **kwargs):
        # Get project first
        self.object = self.get_object()
        project = self.object
        
        # Only creator and leads can manage
        if not (project.creator == request.user or 
                project.members.filter(user=request.user, is_lead=True).exists()):
            messages.error(request, 'You do not have permission to manage this project.')
            return redirect('providers:project_detail', pk=project.pk)
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object
        
        # Get applications by role
        context['applications_by_role'] = {}
        for role in project.roles.filter(status='open').select_related('skill_required'):
            apps = role.applications.filter(status='pending').select_related('applicant')
            if apps.exists():
                context['applications_by_role'][role] = apps
        
        # Forms
        context['milestone_form'] = ProjectMilestoneForm(project=project)
        context['message_form'] = ProjectMessageForm(project=project)
        
        # Milestones
        context['milestones'] = project.milestones.all().select_related('completed_by').prefetch_related('assigned_to')
        
        # Messages
        context['messages'] = project.messages.all().select_related('sender', 'milestone').order_by('-is_pinned', 'created_at')
        
        return context


@login_required
@require_POST
def review_application(request, application_id, action):
    """Review and accept/decline an application."""
    application = get_object_or_404(
        ProjectApplication.objects.select_related('role', 'role__project'),
        pk=application_id
    )
    project = application.role.project
    
    # Check permissions
    if project.creator != request.user and not project.members.filter(user=request.user, is_lead=True).exists():
        messages.error(request, 'You do not have permission to review applications.')
        return redirect('providers:project_detail', pk=project.pk)
    
    if action == 'accept':
        application.status = 'accepted'
        application.reviewed_by = request.user
        application.reviewed_at = timezone.now()
        application.save()
        
        # Fill the role
        application.role.status = 'filled'
        application.role.filled_by = application.applicant
        application.role.filled_at = timezone.now()
        application.role.save()
        
        # Add to team
        ProjectMember.objects.get_or_create(
            project=project,
            user=application.applicant,
            defaults={
                'role': application.role,
                'role_title': application.role.title,
            }
        )
        
        # Check for badge awards
        BadgeAwardService.check_and_award_badges(application.applicant)
        
        # Update project status if all roles filled
        if project.open_roles == 0:
            project.status = 'in_progress'
            project.started_at = timezone.now()
            project.save()
        
        messages.success(request, f'Application accepted! {application.applicant.full_name} has been added to the team.')
    
    elif action == 'decline':
        application.status = 'declined'
        application.reviewed_by = request.user
        application.reviewed_at = timezone.now()
        application.save()
        messages.info(request, 'Application declined.')
    
    return redirect('providers:project_manage', pk=project.pk)


@login_required
@require_POST
def publish_project(request, project_id):
    """Publish a draft project."""
    project = get_object_or_404(CommunityProject, pk=project_id, creator=request.user)
    
    if project.status != 'draft':
        messages.error(request, 'Project is already published.')
        return redirect('providers:project_manage', pk=project.pk)
    
    if project.roles.count() == 0:
        messages.error(request, 'Please add at least one role before publishing.')
        return redirect('providers:project_manage', pk=project.pk)
    
    project.status = 'recruiting'
    project.published_at = timezone.now()
    project.save()
    
    messages.success(request, 'Project published! It is now visible to the community.')
    return redirect('providers:project_detail', pk=project.pk)


@login_required
@require_POST
def create_milestone(request, project_id):
    """Create a project milestone."""
    project = get_object_or_404(CommunityProject, pk=project_id)
    
    # Check permissions
    if not (project.creator == request.user or 
            project.members.filter(user=request.user, is_lead=True).exists()):
        messages.error(request, 'You do not have permission to create milestones.')
        return redirect('providers:project_detail', pk=project.pk)
    
    form = ProjectMilestoneForm(request.POST, project=project)
    if form.is_valid():
        milestone = form.save(commit=False)
        milestone.project = project
        milestone.save()
        form.save_m2m()
        messages.success(request, 'Milestone created!')
    else:
        messages.error(request, 'Please correct the errors below.')
    
    return redirect('providers:project_manage', pk=project.pk)


@login_required
@require_POST
def send_project_message(request, project_id):
    """Send a message in project discussion."""
    project = get_object_or_404(CommunityProject, pk=project_id)
    
    # Check if user is team member
    if not project.members.filter(user=request.user, status='active').exists():
        messages.error(request, 'You must be a team member to send messages.')
        return redirect('providers:project_detail', pk=project.pk)
    
    form = ProjectMessageForm(request.POST, project=project)
    if form.is_valid():
        message = form.save(commit=False)
        message.project = project
        message.sender = request.user
        message.save()
        messages.success(request, 'Message sent!')
    else:
        messages.error(request, 'Please enter a message.')
    
    return redirect('providers:project_manage', pk=project.pk)
