"""
Forms for community project board.
"""

from django import forms
from django.core.validators import MinValueValidator
from decimal import Decimal

from .community_projects import CommunityProject, ProjectRole, ProjectApplication, ProjectMilestone, ProjectMessage
from apps.accounts.modes_models import Skill


class ProjectRoleForm(forms.ModelForm):
    """Form for creating/editing project roles."""
    
    class Meta:
        model = ProjectRole
        fields = [
            'title', 'description', 'skill_required', 'skills_preferred',
            'time_commitment_hours', 'time_commitment_description',
            'experience_level', 'compensation_type', 'compensation_amount',
            'compensation_description'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'e.g., Lead Electrician'
            }),
            'description': forms.Textarea(attrs={
                'class': 'input',
                'rows': 4,
                'placeholder': 'Describe the role and responsibilities...'
            }),
            'skill_required': forms.Select(attrs={'class': 'input'}),
            'skills_preferred': forms.SelectMultiple(attrs={'class': 'input'}),
            'time_commitment_hours': forms.NumberInput(attrs={
                'class': 'input',
                'step': '0.5',
                'placeholder': 'Hours per week/month'
            }),
            'time_commitment_description': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'e.g., 10 hours/week'
            }),
            'experience_level': forms.Select(attrs={'class': 'input'}),
            'compensation_type': forms.Select(attrs={'class': 'input'}),
            'compensation_amount': forms.NumberInput(attrs={
                'class': 'input',
                'step': '0.01',
                'placeholder': 'Amount'
            }),
            'compensation_description': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'e.g., $50/hour, 5 credits, Volunteer'
            }),
        }


class ProjectRoleFormSet(forms.BaseFormSet):
    """Formset for multiple project roles."""
    pass


ProjectRoleFormSet = forms.formset_factory(
    ProjectRoleForm,
    formset=ProjectRoleFormSet,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)


class CommunityProjectForm(forms.ModelForm):
    """Form for creating/editing community projects."""
    
    class Meta:
        model = CommunityProject
        fields = [
            'title', 'description', 'project_type', 'start_date', 'end_date',
            'timeline_description', 'location_city', 'location_state',
            'location_address', 'location_zip', 'is_remote_friendly',
            'compensation_type', 'budget_total', 'featured_image'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'Project title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'input',
                'rows': 6,
                'placeholder': 'Describe your project in detail...'
            }),
            'project_type': forms.Select(attrs={'class': 'input'}),
            'start_date': forms.DateInput(attrs={
                'class': 'input',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'input',
                'type': 'date'
            }),
            'timeline_description': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'e.g., 3-6 months, Ongoing'
            }),
            'location_city': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'City'
            }),
            'location_state': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'State'
            }),
            'location_address': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'Street address (optional)'
            }),
            'location_zip': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'ZIP code'
            }),
            'is_remote_friendly': forms.CheckboxInput(attrs={'class': 'checkbox'}),
            'compensation_type': forms.Select(attrs={'class': 'input'}),
            'budget_total': forms.NumberInput(attrs={
                'class': 'input',
                'step': '0.01',
                'placeholder': 'Total budget'
            }),
            'featured_image': forms.FileInput(attrs={'class': 'input'}),
        }


class ProjectApplicationForm(forms.ModelForm):
    """Form for applying to a project role."""
    
    class Meta:
        model = ProjectApplication
        fields = ['cover_letter', 'relevant_experience']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'class': 'input',
                'rows': 6,
                'placeholder': 'Tell us why you\'re interested and qualified for this role...'
            }),
            'relevant_experience': forms.Textarea(attrs={
                'class': 'input',
                'rows': 4,
                'placeholder': 'Share relevant experience, portfolio links, or examples of your work...'
            }),
        }


class ProjectMilestoneForm(forms.ModelForm):
    """Form for creating/editing project milestones."""
    
    class Meta:
        model = ProjectMilestone
        fields = ['title', 'description', 'due_date', 'assigned_to']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'Milestone title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'input',
                'rows': 3,
                'placeholder': 'Milestone description...'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'input',
                'type': 'date'
            }),
            'assigned_to': forms.SelectMultiple(attrs={'class': 'input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        
        if self.project:
            # Limit assigned_to to project team members
            from django.contrib.auth import get_user_model
            User = get_user_model()
            team_user_ids = self.project.team_members.values_list('user_id', flat=True)
            self.fields['assigned_to'].queryset = User.objects.filter(id__in=team_user_ids)


class ProjectMessageForm(forms.ModelForm):
    """Form for sending project messages."""
    
    class Meta:
        model = ProjectMessage
        fields = ['message', 'milestone']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'input',
                'rows': 4,
                'placeholder': 'Type your message...'
            }),
            'milestone': forms.Select(attrs={'class': 'input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        
        if self.project:
            # Limit milestone to project milestones
            self.fields['milestone'].queryset = self.project.milestones.all()
            self.fields['milestone'].required = False
