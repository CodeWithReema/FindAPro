"""
Forms for multi-mode profile system.
"""

from django import forms
from .modes_models import (
    FreelanceListing, FreelancePortfolioItem, SkillSwapListing, SkillCredit, Skill
)


class FreelanceListingForm(forms.ModelForm):
    """Form for creating/editing freelance listings."""
    
    class Meta:
        model = FreelanceListing
        fields = [
            'title', 'bio', 'headline', 'skills', 'expertise_tags',
            'pricing_type', 'hourly_rate', 'project_rate_min', 'project_rate_max', 'currency',
            'portfolio_url', 'github_url', 'linkedin_url', 'behance_url',
            'availability_status', 'availability_notes', 'timezone',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'e.g., Senior Web Developer'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'input',
                'rows': 6,
                'placeholder': 'Tell potential clients about your experience and expertise...'
            }),
            'headline': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'Short professional headline'
            }),
            'skills': forms.SelectMultiple(attrs={
                'class': 'input',
                'size': '10'
            }),
            'expertise_tags': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'React, Python, UI/UX Design (comma-separated)'
            }),
            'pricing_type': forms.Select(attrs={'class': 'input'}),
            'hourly_rate': forms.NumberInput(attrs={
                'class': 'input',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'project_rate_min': forms.NumberInput(attrs={
                'class': 'input',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'project_rate_max': forms.NumberInput(attrs={
                'class': 'input',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'currency': forms.TextInput(attrs={
                'class': 'input',
                'maxlength': '3',
                'placeholder': 'USD'
            }),
            'portfolio_url': forms.URLInput(attrs={
                'class': 'input',
                'placeholder': 'https://yourportfolio.com'
            }),
            'github_url': forms.URLInput(attrs={
                'class': 'input',
                'placeholder': 'https://github.com/username'
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'input',
                'placeholder': 'https://linkedin.com/in/username'
            }),
            'behance_url': forms.URLInput(attrs={
                'class': 'input',
                'placeholder': 'https://behance.net/username'
            }),
            'availability_status': forms.Select(attrs={'class': 'input'}),
            'availability_notes': forms.Textarea(attrs={
                'class': 'input',
                'rows': 3,
                'placeholder': 'Additional availability information...'
            }),
            'timezone': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'America/New_York'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['skills'].queryset = Skill.objects.filter(is_active=True)
        self.fields['skills'].required = False


class FreelancePortfolioItemForm(forms.ModelForm):
    """Form for adding portfolio items."""
    
    class Meta:
        model = FreelancePortfolioItem
        fields = ['item_type', 'title', 'description', 'image', 'url', 'case_study_content', 'order', 'is_featured']
        widgets = {
            'item_type': forms.Select(attrs={'class': 'input'}),
            'title': forms.TextInput(attrs={'class': 'input'}),
            'description': forms.Textarea(attrs={'class': 'input', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'input'}),
            'url': forms.URLInput(attrs={'class': 'input'}),
            'case_study_content': forms.Textarea(attrs={'class': 'input', 'rows': 10}),
            'order': forms.NumberInput(attrs={'class': 'input', 'min': '0'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'checkbox'}),
        }


FreelancePortfolioItemFormSet = forms.inlineformset_factory(
    FreelanceListing,
    FreelancePortfolioItem,
    form=FreelancePortfolioItemForm,
    extra=1,
    can_delete=True,
    min_num=0,
)


class SkillSwapListingForm(forms.ModelForm):
    """Form for creating/editing skill swap listings."""
    
    class Meta:
        model = SkillSwapListing
        fields = [
            'bio', 'skills_offered', 'skills_wanted',
            'additional_skills_offered', 'additional_skills_wanted',
            'location_preference', 'accepts_remote',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'input',
                'rows': 6,
                'placeholder': 'Tell others about yourself and what you\'re looking for in skill swaps...'
            }),
            'skills_offered': forms.SelectMultiple(attrs={
                'class': 'input',
                'size': '10'
            }),
            'skills_wanted': forms.SelectMultiple(attrs={
                'class': 'input',
                'size': '10'
            }),
            'additional_skills_offered': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'Comma-separated additional skills you offer'
            }),
            'additional_skills_wanted': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'Comma-separated additional skills you want'
            }),
            'location_preference': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'City, State or "Remote"'
            }),
            'accepts_remote': forms.CheckboxInput(attrs={'class': 'checkbox'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['skills_offered'].queryset = Skill.objects.filter(is_active=True)
        self.fields['skills_wanted'].queryset = Skill.objects.filter(is_active=True)
        self.fields['skills_offered'].required = False
        self.fields['skills_wanted'].required = False


class SkillCreditForm(forms.ModelForm):
    """Form for recording skill swap credits."""
    
    class Meta:
        model = SkillCredit
        fields = [
            'to_user', 'transaction_type', 'credits', 'skill_swapped',
            'description', 'swap_date', 'notes'
        ]
        widgets = {
            'to_user': forms.Select(attrs={'class': 'input'}),
            'transaction_type': forms.Select(attrs={'class': 'input'}),
            'credits': forms.NumberInput(attrs={
                'class': 'input',
                'step': '0.5',
                'min': '0',
                'placeholder': '1.0'
            }),
            'skill_swapped': forms.Select(attrs={'class': 'input'}),
            'description': forms.Textarea(attrs={
                'class': 'input',
                'rows': 4,
                'placeholder': 'Describe the skill swap...'
            }),
            'swap_date': forms.DateInput(attrs={
                'class': 'input',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'input',
                'rows': 3,
                'placeholder': 'Additional notes (optional)'
            }),
        }
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user:
            # Filter users who have skill swap listings
            from django.contrib.auth import get_user_model
            User = get_user_model()
            self.fields['to_user'].queryset = User.objects.filter(
                is_skill_swap_active=True
            ).exclude(id=user.id)
        self.fields['skill_swapped'].queryset = Skill.objects.filter(is_active=True)


class ProfileModeToggleForm(forms.Form):
    """Form for toggling profile modes."""
    
    active_mode = forms.ChoiceField(
        choices=[
            ('provider', 'Service Provider'),
            ('freelance', 'Freelance'),
            ('skill_swap', 'Skill Swap'),
        ],
        widget=forms.Select(attrs={'class': 'input'}),
        required=False
    )
    
    enable_freelance = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'checkbox'})
    )
    
    enable_skill_swap = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'checkbox'})
    )
