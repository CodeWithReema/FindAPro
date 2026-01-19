from django import forms
from .models import ServiceCategory, QuoteRequest, ServiceProvider, BusinessHours, ServiceArea, ProviderCertification


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


# ============================================================================
# Provider Profile Creation Forms (Multi-Step)
# ============================================================================

class ProviderBasicInfoForm(forms.ModelForm):
    """Step 1: Basic Information Form."""
    
    class Meta:
        model = ServiceProvider
        fields = ['name', 'category', 'tagline', 'description', 'skills']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'Your business name',
            }),
            'category': forms.Select(attrs={
                'class': 'input',
            }),
            'tagline': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'A short tagline for your business (optional)',
            }),
            'description': forms.Textarea(attrs={
                'class': 'input',
                'rows': 5,
                'placeholder': 'Describe your business, services, and what makes you unique...',
            }),
            'skills': forms.Textarea(attrs={
                'class': 'input',
                'rows': 3,
                'placeholder': 'List your skills separated by commas (e.g., Plumbing, HVAC, Electrical)',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = ServiceCategory.objects.filter(is_active=True)
        self.fields['category'].empty_label = 'Select a category'
        self.fields['name'].required = True
        self.fields['category'].required = True
        self.fields['description'].required = True
        self.fields['skills'].required = True


class ProviderContactLocationForm(forms.ModelForm):
    """Step 2: Contact & Location Form."""
    
    class Meta:
        model = ServiceProvider
        fields = ['email', 'phone', 'website', 'address', 'city', 'state', 'zip_code']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'input',
                'placeholder': 'business@example.com',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': '(555) 123-4567',
            }),
            'website': forms.URLInput(attrs={
                'class': 'input',
                'placeholder': 'https://yourwebsite.com (optional)',
            }),
            'address': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': '123 Main Street (optional)',
            }),
            'city': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'City',
            }),
            'state': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'State',
            }),
            'zip_code': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'ZIP Code',
            }),
        }
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user and not self.instance.pk:
            # Pre-fill email from user account
            self.fields['email'].initial = user.email
        self.fields['phone'].required = True
        self.fields['city'].required = True
        self.fields['state'].required = True
        self.fields['zip_code'].required = True


class ProviderBusinessDetailsForm(forms.ModelForm):
    """Step 3: Business Details Form."""
    
    class Meta:
        model = ServiceProvider
        fields = ['pricing_range', 'years_experience']
        widgets = {
            'pricing_range': forms.Select(attrs={
                'class': 'input',
            }),
            'years_experience': forms.NumberInput(attrs={
                'class': 'input',
                'min': '0',
                'placeholder': '0',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pricing_range'].required = True
        self.fields['years_experience'].required = True


class BusinessHoursForm(forms.ModelForm):
    """Form for business hours (part of Step 3)."""
    
    class Meta:
        model = BusinessHours
        fields = [
            'monday_open', 'monday_close', 'monday_closed',
            'tuesday_open', 'tuesday_close', 'tuesday_closed',
            'wednesday_open', 'wednesday_close', 'wednesday_closed',
            'thursday_open', 'thursday_close', 'thursday_closed',
            'friday_open', 'friday_close', 'friday_closed',
            'saturday_open', 'saturday_close', 'saturday_closed',
            'sunday_open', 'sunday_close', 'sunday_closed',
            'notes',
        ]
        widgets = {
            'monday_open': forms.TimeInput(attrs={'type': 'time', 'class': 'input'}),
            'monday_close': forms.TimeInput(attrs={'type': 'time', 'class': 'input'}),
            'tuesday_open': forms.TimeInput(attrs={'type': 'time', 'class': 'input'}),
            'tuesday_close': forms.TimeInput(attrs={'type': 'time', 'class': 'input'}),
            'wednesday_open': forms.TimeInput(attrs={'type': 'time', 'class': 'input'}),
            'wednesday_close': forms.TimeInput(attrs={'type': 'time', 'class': 'input'}),
            'thursday_open': forms.TimeInput(attrs={'type': 'time', 'class': 'input'}),
            'thursday_close': forms.TimeInput(attrs={'type': 'time', 'class': 'input'}),
            'friday_open': forms.TimeInput(attrs={'type': 'time', 'class': 'input'}),
            'friday_close': forms.TimeInput(attrs={'type': 'time', 'class': 'input'}),
            'saturday_open': forms.TimeInput(attrs={'type': 'time', 'class': 'input'}),
            'saturday_close': forms.TimeInput(attrs={'type': 'time', 'class': 'input'}),
            'sunday_open': forms.TimeInput(attrs={'type': 'time', 'class': 'input'}),
            'sunday_close': forms.TimeInput(attrs={'type': 'time', 'class': 'input'}),
            'notes': forms.Textarea(attrs={
                'class': 'input',
                'rows': 3,
                'placeholder': 'Additional notes about availability (optional)',
            }),
        }


class ServiceAreaForm(forms.ModelForm):
    """Form for adding service areas (part of Step 3)."""
    
    class Meta:
        model = ServiceArea
        fields = ['zip_code', 'city', 'state', 'radius_miles', 'is_primary']
        widgets = {
            'zip_code': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'ZIP Code',
            }),
            'city': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'City',
            }),
            'state': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'State',
            }),
            'radius_miles': forms.NumberInput(attrs={
                'class': 'input',
                'min': '1',
                'placeholder': '25',
            }),
            'is_primary': forms.CheckboxInput(attrs={
                'class': 'checkbox',
            }),
        }


ServiceAreaFormSet = forms.inlineformset_factory(
    ServiceProvider,
    ServiceArea,
    form=ServiceAreaForm,
    extra=1,
    can_delete=True,
    min_num=0,
)


class ProviderMediaForm(forms.ModelForm):
    """Step 4: Media & Portfolio Form."""
    
    class Meta:
        model = ServiceProvider
        fields = ['logo', 'image']
        widgets = {
            'logo': forms.FileInput(attrs={
                'class': 'input',
                'accept': 'image/*',
            }),
            'image': forms.FileInput(attrs={
                'class': 'input',
                'accept': 'image/*',
            }),
        }


class ProviderAvailabilityForm(forms.ModelForm):
    """Step 5: Availability & Emergency Form."""
    
    class Meta:
        model = ServiceProvider
        fields = ['accepts_emergency', 'emergency_rate_info', 'is_available_now']
        widgets = {
            'accepts_emergency': forms.CheckboxInput(attrs={
                'class': 'checkbox',
            }),
            'emergency_rate_info': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'e.g., "25% premium for emergencies"',
            }),
            'is_available_now': forms.CheckboxInput(attrs={
                'class': 'checkbox',
            }),
        }
