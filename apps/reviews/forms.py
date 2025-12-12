"""
Forms for reviews app.
"""

from django import forms
from .models import ProviderReview


class ReviewForm(forms.ModelForm):
    """Form for creating/editing reviews."""
    
    RATING_CHOICES = [(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)]
    
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'sr-only peer'
        })
    )
    
    class Meta:
        model = ProviderReview
        fields = ['rating', 'title', 'comment', 'would_recommend', 'service_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'Summarize your experience'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'input',
                'rows': 5,
                'placeholder': 'Tell others about your experience with this provider...'
            }),
            'would_recommend': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-brand-600 rounded focus:ring-brand-500'
            }),
            'service_date': forms.DateInput(attrs={
                'class': 'input',
                'type': 'date'
            }),
        }
    
    def clean_rating(self):
        rating = int(self.cleaned_data['rating'])
        if rating < 1 or rating > 5:
            raise forms.ValidationError('Rating must be between 1 and 5')
        return rating

