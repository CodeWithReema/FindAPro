"""
Forms for matching system.
"""

from django import forms
from .matching_models import Match


class MatchFilterForm(forms.Form):
    """Form for filtering matches."""
    
    MATCH_TYPE_CHOICES = [
        ('all', 'All Types'),
        ('skill_swap', 'Skill Swap'),
        ('freelance_collab', 'Freelance Collaboration'),
    ]
    
    STATUS_CHOICES = [
        ('all', 'All Statuses'),
        ('pending', 'Pending'),
        ('viewed', 'Viewed'),
        ('interested', 'Interested'),
        ('connected', 'Connected'),
    ]
    
    match_type = forms.ChoiceField(
        choices=MATCH_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'input'})
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'input'})
    )
