from django import forms
from .models import ServiceCategory, QuoteRequest


class QuoteRequestForm(forms.ModelForm):
    """Form for users to request a quote from a provider."""
    
    class Meta:
        model = QuoteRequest
        fields = ['title', 'description', 'timeline', 'budget', 'preferred_contact', 'phone', 'service_address', 'service_city', 'service_zip']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Kitchen sink repair',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 5,
                'placeholder': 'Describe the work you need done, including any relevant details...',
            }),
            'timeline': forms.Select(attrs={
                'class': 'form-select',
            }),
            'budget': forms.Select(attrs={
                'class': 'form-select',
            }),
            'preferred_contact': forms.Select(attrs={
                'class': 'form-select',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '(555) 123-4567',
            }),
            'service_address': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '123 Main St',
            }),
            'service_city': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'City',
            }),
            'service_zip': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'ZIP Code',
            }),
        }
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user


class QuoteResponseForm(forms.ModelForm):
    """Form for providers to respond to quote requests."""
    
    class Meta:
        model = QuoteRequest
        fields = ['quote_amount', 'quote_message']
        widgets = {
            'quote_amount': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
            }),
            'quote_message': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Add any notes about the quote, availability, or questions for the customer...',
            }),
        }


class MatchingQuizForm(forms.Form):
    """Multi-step quiz form for matching users with providers."""
    
    URGENCY_CHOICES = [
        ('emergency', 'Emergency - I need help TODAY'),
        ('this_week', 'This week'),
        ('this_month', 'Within the next month'),
        ('flexible', 'No rush - just exploring'),
    ]
    
    BUDGET_CHOICES = [
        ('budget', 'Budget-friendly ($)'),
        ('mid', 'Mid-range ($$)'),
        ('premium', 'Premium ($$$)'),
        ('any', "Price isn't a concern"),
    ]
    
    PRIORITY_CHOICES = [
        ('quality', 'Quality - I want the best work possible'),
        ('speed', 'Speed - I need it done fast'),
        ('price', 'Price - I want the best deal'),
        ('reviews', 'Reviews - I trust what others say'),
    ]
    
    # Step 1: Category
    category = forms.ModelChoiceField(
        queryset=ServiceCategory.objects.all(),
        widget=forms.RadioSelect(attrs={'class': 'quiz-radio'}),
        empty_label=None,
        required=True,
    )
    
    # Step 2: Location
    city = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'quiz-input',
            'placeholder': 'Enter your city...',
            'autocomplete': 'off',
        })
    )
    
    # Step 3: Urgency
    urgency = forms.ChoiceField(
        choices=URGENCY_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'quiz-radio'}),
        required=True,
    )
    
    # Step 4: Budget
    budget = forms.ChoiceField(
        choices=BUDGET_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'quiz-radio'}),
        required=True,
    )
    
    # Step 5: Priority
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'quiz-radio'}),
        required=True,
    )
