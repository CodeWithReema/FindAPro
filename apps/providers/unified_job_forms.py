"""
Forms for unified job/booking system.
"""

from django import forms
from django.core.validators import MinValueValidator
from decimal import Decimal

from .unified_jobs import UnifiedJob, JobProposal, JobMessage


class UnifiedJobRequestForm(forms.ModelForm):
    """Unified form for creating job requests (paid, credit, or barter)."""
    
    PAYMENT_TYPE_CHOICES = [
        ('paid', 'Paid Job'),
        ('credit', 'Credit-Based Swap'),
        ('barter', 'Barter Proposal'),
    ]
    
    payment_type = forms.ChoiceField(
        choices=PAYMENT_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'payment-type-select'}),
        label='Job Type'
    )
    
    # Paid job fields
    budget_min = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0'),
        widget=forms.NumberInput(attrs={
            'class': 'input',
            'placeholder': 'Minimum budget',
            'step': '0.01'
        }),
        label='Minimum Budget ($)'
    )
    budget_max = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0'),
        widget=forms.NumberInput(attrs={
            'class': 'input',
            'placeholder': 'Maximum budget',
            'step': '0.01'
        }),
        label='Maximum Budget ($)'
    )
    
    # Credit job fields
    credits_requested = forms.DecimalField(
        required=False,
        max_digits=5,
        decimal_places=2,
        min_value=Decimal('0.5'),
        widget=forms.NumberInput(attrs={
            'class': 'input',
            'placeholder': 'Hours (1 hour = 1 credit)',
            'step': '0.5'
        }),
        label='Credits Requested (hours)'
    )
    
    # Barter fields
    barter_offer = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'input',
            'rows': 3,
            'placeholder': 'What you offer in exchange (e.g., I\'ll design your logo if you write my website copy)'
        }),
        label='What You Offer'
    )
    barter_request = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'input',
            'rows': 3,
            'placeholder': 'What you want in exchange'
        }),
        label='What You Want'
    )
    
    class Meta:
        model = UnifiedJob
        fields = [
            'payment_type', 'title', 'description', 'timeline',
            'is_emergency', 'service_address', 'service_city',
            'service_state', 'service_zip', 'preferred_contact', 'phone',
            'budget_min', 'budget_max', 'credits_requested',
            'barter_offer', 'barter_request'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'e.g., Kitchen sink repair'
            }),
            'description': forms.Textarea(attrs={
                'class': 'input',
                'rows': 5,
                'placeholder': 'Describe the work you need done...'
            }),
            'timeline': forms.Select(attrs={'class': 'input'}),
            'is_emergency': forms.CheckboxInput(attrs={'class': 'checkbox'}),
            'service_address': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': '123 Main St'
            }),
            'service_city': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'City'
            }),
            'service_state': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'State'
            }),
            'service_zip': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'ZIP Code'
            }),
            'preferred_contact': forms.Select(attrs={'class': 'input'}),
            'phone': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': '(555) 123-4567'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.provider = kwargs.pop('provider', None)
        super().__init__(*args, **kwargs)
        
        # Set initial payment type based on provider preferences
        if self.provider:
            if hasattr(self.provider, 'provider_profile'):
                profile = self.provider.provider_profile
                if profile.accepts_credit_jobs and profile.accepts_barter:
                    # Show all options
                    pass
                elif profile.accepts_credit_jobs:
                    self.fields['payment_type'].choices = [
                        ('paid', 'Paid Job'),
                        ('credit', 'Credit-Based Swap'),
                    ]
                elif profile.accepts_barter:
                    self.fields['payment_type'].choices = [
                        ('paid', 'Paid Job'),
                        ('barter', 'Barter Proposal'),
                    ]
    
    def clean(self):
        cleaned_data = super().clean()
        payment_type = cleaned_data.get('payment_type')
        
        # Validate based on payment type
        if payment_type == 'paid':
            if not cleaned_data.get('budget_min') and not cleaned_data.get('budget_max'):
                raise forms.ValidationError({
                    'budget_min': 'Please specify at least a minimum or maximum budget for paid jobs.'
                })
            # Clear credit and barter fields
            cleaned_data['credits_requested'] = None
            cleaned_data['barter_offer'] = ''
            cleaned_data['barter_request'] = ''
        
        elif payment_type == 'credit':
            if not cleaned_data.get('credits_requested'):
                raise forms.ValidationError({
                    'credits_requested': 'Please specify the number of credits (hours) requested.'
                })
            # Clear paid and barter fields
            cleaned_data['budget_min'] = None
            cleaned_data['budget_max'] = None
            cleaned_data['barter_offer'] = ''
            cleaned_data['barter_request'] = ''
        
        elif payment_type == 'barter':
            if not cleaned_data.get('barter_offer') or not cleaned_data.get('barter_request'):
                raise forms.ValidationError({
                    'barter_offer': 'Please specify both what you offer and what you want for barter proposals.',
                    'barter_request': 'Please specify both what you offer and what you want for barter proposals.'
                })
            # Clear paid and credit fields
            cleaned_data['budget_min'] = None
            cleaned_data['budget_max'] = None
            cleaned_data['credits_requested'] = None
        
        return cleaned_data


class JobProposalForm(forms.ModelForm):
    """Form for creating job proposals and counter-offers."""
    
    class Meta:
        model = JobProposal
        fields = [
            'message', 'proposed_amount', 'proposed_credits',
            'proposed_barter_offer', 'proposed_barter_request'
        ]
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'input',
                'rows': 4,
                'placeholder': 'Your proposal message...'
            }),
            'proposed_amount': forms.NumberInput(attrs={
                'class': 'input',
                'placeholder': 'Proposed amount ($)',
                'step': '0.01'
            }),
            'proposed_credits': forms.NumberInput(attrs={
                'class': 'input',
                'placeholder': 'Proposed credits (hours)',
                'step': '0.5'
            }),
            'proposed_barter_offer': forms.Textarea(attrs={
                'class': 'input',
                'rows': 2,
                'placeholder': 'What you offer...'
            }),
            'proposed_barter_request': forms.Textarea(attrs={
                'class': 'input',
                'rows': 2,
                'placeholder': 'What you want...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.job = kwargs.pop('job', None)
        self.proposed_by = kwargs.pop('proposed_by', None)
        super().__init__(*args, **kwargs)
        
        # Show/hide fields based on job payment type
        if self.job:
            if self.job.payment_type == 'paid':
                self.fields['proposed_credits'].widget = forms.HiddenInput()
                self.fields['proposed_barter_offer'].widget = forms.HiddenInput()
                self.fields['proposed_barter_request'].widget = forms.HiddenInput()
            elif self.job.payment_type == 'credit':
                self.fields['proposed_amount'].widget = forms.HiddenInput()
                self.fields['proposed_barter_offer'].widget = forms.HiddenInput()
                self.fields['proposed_barter_request'].widget = forms.HiddenInput()
            elif self.job.payment_type == 'barter':
                self.fields['proposed_amount'].widget = forms.HiddenInput()
                self.fields['proposed_credits'].widget = forms.HiddenInput()
    
    def clean(self):
        cleaned_data = super().clean()
        
        if not self.job:
            return cleaned_data
        
        # Validate based on job payment type
        if self.job.payment_type == 'paid':
            if not cleaned_data.get('proposed_amount'):
                raise forms.ValidationError({
                    'proposed_amount': 'Please specify a proposed amount for paid jobs.'
                })
        
        elif self.job.payment_type == 'credit':
            if not cleaned_data.get('proposed_credits'):
                raise forms.ValidationError({
                    'proposed_credits': 'Please specify proposed credits (hours) for credit-based jobs.'
                })
        
        elif self.job.payment_type == 'barter':
            if not cleaned_data.get('proposed_barter_offer') or not cleaned_data.get('proposed_barter_request'):
                raise forms.ValidationError({
                    'proposed_barter_offer': 'Please specify both offer and request for barter proposals.',
                    'proposed_barter_request': 'Please specify both offer and request for barter proposals.'
                })
        
        return cleaned_data


class JobMessageForm(forms.ModelForm):
    """Form for sending messages in job threads."""
    
    class Meta:
        model = JobMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'input',
                'rows': 4,
                'placeholder': 'Type your message...'
            }),
        }
