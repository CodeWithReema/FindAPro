"""
Views for providers app - Template views.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Avg, Count
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify

from .models import (
    ServiceCategory, ServiceProvider, FavoriteProvider, QuoteRequest,
    BusinessHours, ServiceArea, ProviderCertification
)
from .forms import (
    QuoteRequestForm, QuoteResponseForm, MatchingQuizForm,
    ProviderBasicInfoForm, ProviderContactLocationForm, ProviderBusinessDetailsForm,
    BusinessHoursForm, ServiceAreaForm, ServiceAreaFormSet,
    ProviderMediaForm, ProviderAvailabilityForm
)


class ProviderSearchView(ListView):
    """Search and filter providers."""
    
    model = ServiceProvider
    template_name = 'providers/search_results.html'
    context_object_name = 'providers'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = ServiceProvider.objects.filter(is_active=True).select_related('category')
        
        # Search query
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(skills__icontains=query) |
                Q(tagline__icontains=query)
            )
        
        # Filter by category
        category = self.request.GET.get('category', '').strip()
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Filter by city
        city = self.request.GET.get('city', '').strip()
        if city:
            queryset = queryset.filter(city__icontains=city)
        
        # Filter by state
        state = self.request.GET.get('state', '').strip()
        if state:
            queryset = queryset.filter(state__icontains=state)
        
        # Filter by zip code
        zip_code = self.request.GET.get('zip', '').strip()
        if zip_code:
            queryset = queryset.filter(zip_code__startswith=zip_code)
        
        # Filter by pricing
        pricing = self.request.GET.get('pricing', '').strip()
        if pricing:
            queryset = queryset.filter(pricing_range=pricing)
        
        # Filter verified only
        verified = self.request.GET.get('verified', '').strip()
        if verified == 'true':
            queryset = queryset.filter(is_verified=True)
        
        # Sorting
        sort = self.request.GET.get('sort', 'rating')
        if sort == 'rating':
            queryset = queryset.annotate(
                avg_rating=Avg('reviews__rating')
            ).order_by('-avg_rating', '-is_featured')
        elif sort == 'reviews':
            queryset = queryset.annotate(
                num_reviews=Count('reviews')
            ).order_by('-num_reviews', '-is_featured')
        elif sort == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort == 'name':
            queryset = queryset.order_by('name')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ServiceCategory.objects.filter(is_active=True)
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_city'] = self.request.GET.get('city', '')
        context['selected_state'] = self.request.GET.get('state', '')
        context['selected_zip'] = self.request.GET.get('zip', '')
        context['selected_pricing'] = self.request.GET.get('pricing', '')
        context['verified_only'] = self.request.GET.get('verified', '')
        context['sort_by'] = self.request.GET.get('sort', 'rating')
        context['total_results'] = self.get_queryset().count()
        return context


class ProviderDetailView(DetailView):
    """Provider profile detail view."""
    
    model = ServiceProvider
    template_name = 'providers/provider_detail.html'
    context_object_name = 'provider'
    
    def get_queryset(self):
        return ServiceProvider.objects.filter(is_active=True).select_related('category')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        provider = self.object
        
        # Get reviews
        context['reviews'] = provider.reviews.select_related('user').order_by('-created_at')[:10]
        
        # Get related providers in same category
        context['related_providers'] = ServiceProvider.objects.filter(
            category=provider.category,
            is_active=True
        ).exclude(id=provider.id)[:4]
        
        # Rating distribution
        context['rating_distribution'] = self._get_rating_distribution(provider)
        
        # Check if user has favorited this provider
        context['is_favorited'] = False
        if self.request.user.is_authenticated:
            context['is_favorited'] = FavoriteProvider.objects.filter(
                user=self.request.user,
                provider=provider
            ).exists()
        
        return context
    
    def _get_rating_distribution(self, provider):
        """Calculate rating distribution for charts."""
        distribution = {}
        total = provider.review_count
        
        for i in range(1, 6):
            count = provider.reviews.filter(rating=i).count()
            percentage = (count / total * 100) if total > 0 else 0
            distribution[i] = {
                'count': count,
                'percentage': round(percentage)
            }
        
        return distribution


class CategoryListView(ListView):
    """List all service categories."""
    
    model = ServiceCategory
    template_name = 'providers/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return ServiceCategory.objects.filter(is_active=True).annotate(
            provider_count_annotated=Count('providers', filter=Q(providers__is_active=True))
        )


class CategoryDetailView(DetailView):
    """Category detail with providers."""
    
    model = ServiceCategory
    template_name = 'providers/category_detail.html'
    context_object_name = 'category'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['providers'] = ServiceProvider.objects.filter(
            category=self.object,
            is_active=True
        ).annotate(
            avg_rating=Avg('reviews__rating')
        ).order_by('-is_featured', '-avg_rating')[:12]
        return context


class FavoriteListView(LoginRequiredMixin, ListView):
    """List user's favorite providers."""
    
    model = FavoriteProvider
    template_name = 'providers/favorites.html'
    context_object_name = 'favorites'
    
    def get_queryset(self):
        return FavoriteProvider.objects.filter(
            user=self.request.user
        ).select_related('provider', 'provider__category')


@require_POST
@login_required
def toggle_favorite(request, provider_id):
    """Toggle favorite status for a provider (AJAX)."""
    provider = get_object_or_404(ServiceProvider, id=provider_id, is_active=True)
    
    favorite, created = FavoriteProvider.objects.get_or_create(
        user=request.user,
        provider=provider
    )
    
    if not created:
        # Already existed, so remove it
        favorite.delete()
        is_favorited = False
    else:
        is_favorited = True
    
    return JsonResponse({
        'success': True,
        'is_favorited': is_favorited,
        'message': 'Added to favorites' if is_favorited else 'Removed from favorites'
    })


class QuoteRequestCreateView(LoginRequiredMixin, CreateView):
    """Create a quote request for a provider."""
    
    model = QuoteRequest
    form_class = QuoteRequestForm
    template_name = 'providers/quote_request_form.html'
    
    def get_provider(self):
        return get_object_or_404(ServiceProvider, slug=self.kwargs['slug'], is_active=True)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['provider'] = self.get_provider()
        return context
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.provider = self.get_provider()
        messages.success(self.request, 'Your quote request has been sent! The provider will respond soon.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('providers:my_quotes')


class MyQuotesView(LoginRequiredMixin, ListView):
    """View user's quote requests."""
    
    model = QuoteRequest
    template_name = 'providers/my_quotes.html'
    context_object_name = 'quotes'
    
    def get_queryset(self):
        return QuoteRequest.objects.filter(
            user=self.request.user
        ).select_related('provider', 'provider__category').order_by('-created_at')


class ProviderQuotesView(LoginRequiredMixin, ListView):
    """View quote requests received by provider."""
    
    model = QuoteRequest
    template_name = 'providers/provider_quotes.html'
    context_object_name = 'quotes'
    
    def get_queryset(self):
        # Check if user has a provider profile
        if not hasattr(self.request.user, 'provider_profile'):
            return QuoteRequest.objects.none()
        
        return QuoteRequest.objects.filter(
            provider=self.request.user.provider_profile
        ).select_related('user').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request.user, 'provider_profile'):
            context['pending_count'] = self.get_queryset().filter(status='pending').count()
        return context


@login_required
def quote_detail(request, pk):
    """View and respond to a quote request."""
    quote = get_object_or_404(QuoteRequest, pk=pk)
    
    # Check permissions
    is_requester = quote.user == request.user
    is_provider = hasattr(request.user, 'provider_profile') and quote.provider == request.user.provider_profile
    
    if not is_requester and not is_provider:
        messages.error(request, "You don't have permission to view this quote.")
        return redirect('core:home')
    
    # Mark as viewed if provider is viewing for the first time
    if is_provider and quote.status == 'pending':
        quote.status = 'viewed'
        quote.save()
    
    # Handle provider response
    if request.method == 'POST' and is_provider:
        form = QuoteResponseForm(request.POST, instance=quote)
        if form.is_valid():
            quote = form.save(commit=False)
            quote.status = 'quoted'
            quote.quoted_at = timezone.now()
            quote.save()
            messages.success(request, 'Your quote has been sent to the customer!')
            return redirect('providers:provider_quotes')
    else:
        form = QuoteResponseForm(instance=quote)
    
    return render(request, 'providers/quote_detail.html', {
        'quote': quote,
        'form': form,
        'is_requester': is_requester,
        'is_provider': is_provider,
    })


@login_required
@require_POST
def update_quote_status(request, pk, status):
    """Update quote status (accept/decline)."""
    quote = get_object_or_404(QuoteRequest, pk=pk, user=request.user)
    
    if status in ['accepted', 'declined'] and quote.status == 'quoted':
        quote.status = status
        quote.save()
        
        if status == 'accepted':
            messages.success(request, 'You have accepted the quote! The provider will be in touch soon.')
        else:
            messages.info(request, 'You have declined the quote.')
    
    return redirect('providers:my_quotes')


def smart_match_quiz(request):
    """
    Smart Matching Quiz - Interactive questionnaire to find the perfect provider.
    Handles both the multi-step form and results display.
    """
    if request.method == 'POST':
        form = MatchingQuizForm(request.POST)
        if form.is_valid():
            # Get form data
            category = form.cleaned_data['category']
            city = form.cleaned_data['city']
            urgency = form.cleaned_data['urgency']
            budget = form.cleaned_data['budget']
            priority = form.cleaned_data['priority']
            
            # Find matching providers
            matches = find_matching_providers(category, city, urgency, budget, priority)
            
            return render(request, 'providers/quiz_results.html', {
                'matches': matches,
                'category': category,
                'city': city,
                'urgency': urgency,
                'budget': budget,
                'priority': priority,
            })
    else:
        form = MatchingQuizForm()
    
    categories = ServiceCategory.objects.filter(is_active=True)
    
    return render(request, 'providers/smart_match_quiz.html', {
        'form': form,
        'categories': categories,
    })


def compare_providers(request):
    """
    Compare up to 3 providers side by side.
    Provider IDs passed as comma-separated query param.
    """
    provider_ids = request.GET.get('ids', '')
    
    if not provider_ids:
        # No providers selected, show empty state
        return render(request, 'providers/compare.html', {
            'providers': [],
            'categories': ServiceCategory.objects.filter(is_active=True),
        })
    
    # Parse IDs and fetch providers
    try:
        ids = [int(id.strip()) for id in provider_ids.split(',') if id.strip()][:3]
    except ValueError:
        ids = []
    
    providers = ServiceProvider.objects.filter(
        id__in=ids,
        is_active=True
    ).select_related('category').annotate(
        avg_rating=Avg('reviews__rating'),
        review_count_val=Count('reviews')
    )
    
    # Build comparison data
    comparison_data = []
    for provider in providers:
        comparison_data.append({
            'provider': provider,
            'rating': provider.avg_rating or 0,
            'reviews': provider.review_count_val or 0,
            'skills': provider.skills_list[:5],  # Top 5 skills
        })
    
    return render(request, 'providers/compare.html', {
        'providers': comparison_data,
        'provider_ids': ','.join(str(id) for id in ids),
    })


def emergency_mode(request):
    """
    Emergency Mode - Find available providers for urgent requests.
    Shows only providers who accept emergencies and are available now.
    """
    categories = ServiceCategory.objects.filter(is_active=True)
    
    # Get filter parameters
    category_slug = request.GET.get('category', '')
    city = request.GET.get('city', '').strip()
    
    # Base queryset - only emergency-ready providers
    providers = ServiceProvider.objects.filter(
        is_active=True,
        accepts_emergency=True
    ).select_related('category').annotate(
        avg_rating=Avg('reviews__rating'),
        review_count_val=Count('reviews')
    )
    
    # Filter by category
    if category_slug:
        providers = providers.filter(category__slug=category_slug)
    
    # Filter by city
    if city:
        providers = providers.filter(city__icontains=city)
    
    # Sort: Available now first, then by rating
    providers = providers.order_by('-is_available_now', '-avg_rating', '-is_verified')
    
    # Separate available now vs others
    available_now = [p for p in providers if p.is_available_now]
    available_soon = [p for p in providers if not p.is_available_now]
    
    return render(request, 'providers/emergency_mode.html', {
        'categories': categories,
        'available_now': available_now,
        'available_soon': available_soon,
        'selected_category': category_slug,
        'selected_city': city,
        'total_count': len(available_now) + len(available_soon),
    })


def find_matching_providers(category, city, urgency, budget, priority):
    """
    Score and rank providers based on quiz answers.
    Returns top matches with match scores.
    """
    # Base queryset
    providers = ServiceProvider.objects.filter(
        category=category,
        is_active=True
    ).select_related('category').annotate(
        avg_rating=Avg('reviews__rating'),
        review_count_val=Count('reviews')
    )
    
    # Filter by city (flexible matching)
    city_matches = providers.filter(city__icontains=city)
    if city_matches.exists():
        providers = city_matches
    
    # Budget mapping to pricing_range
    budget_map = {
        'budget': ['$'],
        'mid': ['$', '$$'],
        'premium': ['$$', '$$$'],
        'any': ['$', '$$', '$$$'],
    }
    
    if budget in budget_map:
        providers = providers.filter(pricing_range__in=budget_map[budget])
    
    # Score each provider
    scored_providers = []
    for provider in providers:
        score = calculate_match_score(provider, urgency, budget, priority)
        scored_providers.append({
            'provider': provider,
            'score': score,
            'match_percentage': min(round(score * 10), 99),  # Convert to percentage (max 99%)
            'match_reasons': get_match_reasons(provider, urgency, budget, priority),
        })
    
    # Sort by score descending
    scored_providers.sort(key=lambda x: x['score'], reverse=True)
    
    # Return top 5 matches
    return scored_providers[:5]


def calculate_match_score(provider, urgency, budget, priority):
    """
    Calculate a match score (0-10) based on provider attributes and user preferences.
    """
    score = 5.0  # Base score
    
    # Rating bonus (up to +2)
    if provider.avg_rating:
        score += (provider.avg_rating - 3) * 0.5  # 5-star = +1, 4-star = +0.5
    
    # Review count bonus (up to +1)
    review_count = provider.review_count_val or 0
    if review_count >= 10:
        score += 1
    elif review_count >= 5:
        score += 0.5
    
    # Verified bonus
    if provider.is_verified:
        score += 0.5
    
    # Featured bonus
    if provider.is_featured:
        score += 0.3
    
    # Priority-based bonuses
    if priority == 'quality':
        # Prioritize rating and verified status
        if provider.avg_rating and provider.avg_rating >= 4.5:
            score += 1
        if provider.is_verified:
            score += 0.5
    
    elif priority == 'speed':
        # Prioritize experience (faster turnaround assumed)
        if provider.years_experience and provider.years_experience >= 5:
            score += 1
    
    elif priority == 'price':
        # Prioritize budget-friendly
        if provider.pricing_range == '$':
            score += 1
        elif provider.pricing_range == '$$':
            score += 0.5
    
    elif priority == 'reviews':
        # Prioritize review count
        if review_count >= 15:
            score += 1.5
        elif review_count >= 8:
            score += 1
    
    # Urgency bonus (verified providers for emergencies)
    if urgency == 'emergency' and provider.is_verified:
        score += 0.5
    
    return score


def get_match_reasons(provider, urgency, budget, priority):
    """
    Generate human-readable reasons why this provider matches.
    """
    reasons = []
    
    # Rating
    if provider.avg_rating:
        if provider.avg_rating >= 4.5:
            reasons.append(f"⭐ Excellent rating ({provider.avg_rating:.1f}/5)")
        elif provider.avg_rating >= 4.0:
            reasons.append(f"⭐ Great rating ({provider.avg_rating:.1f}/5)")
    
    # Reviews
    review_count = provider.review_count_val or 0
    if review_count >= 10:
        reasons.append(f"💬 {review_count} verified reviews")
    elif review_count >= 5:
        reasons.append(f"💬 {review_count} reviews")
    
    # Verified
    if provider.is_verified:
        reasons.append("✓ Verified professional")
    
    # Experience
    if provider.years_experience:
        if provider.years_experience >= 10:
            reasons.append(f"🏆 {provider.years_experience}+ years experience")
        elif provider.years_experience >= 5:
            reasons.append(f"📅 {provider.years_experience} years experience")
    
    # Price match
    if budget == 'budget' and provider.pricing_range == '$':
        reasons.append("💰 Budget-friendly pricing")
    elif budget == 'premium' and provider.pricing_range == '$$$':
        reasons.append("✨ Premium service tier")
    
    # Priority match
    if priority == 'quality' and provider.avg_rating and provider.avg_rating >= 4.5:
        reasons.append("🎯 Top quality in category")
    elif priority == 'speed' and provider.years_experience and provider.years_experience >= 5:
        reasons.append("⚡ Experienced & efficient")
    elif priority == 'reviews' and review_count >= 10:
        reasons.append("👥 Highly reviewed")
    
    # Featured
    if provider.is_featured:
        reasons.append("🌟 Featured provider")
    
    return reasons[:4]  # Return max 4 reasons


# ============================================================================
# Provider Profile Creation Views
# ============================================================================

class JoinAsProView(LoginRequiredMixin, TemplateView):
    """Landing page for users to join as a professional."""
    
    template_name = 'providers/join_as_pro.html'
    
    def dispatch(self, request, *args, **kwargs):
        # If user already has a provider profile, redirect to edit
        if hasattr(request.user, 'provider_profile'):
            messages.info(request, 'You already have a provider profile. You can edit it below.')
            return redirect('providers:profile_edit')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ServiceCategory.objects.filter(is_active=True)
        return context


@login_required
def provider_profile_create(request):
    """
    Multi-step provider profile creation wizard.
    Handles 5 steps of profile creation with session-based state management.
    """
    # Check if user already has a profile
    if hasattr(request.user, 'provider_profile'):
        messages.info(request, 'You already have a provider profile.')
        return redirect('providers:profile_edit')
    
    # Get current step from session or default to 1
    current_step = int(request.session.get('profile_create_step', 1))
    total_steps = 5
    
    # Handle step navigation
    if 'step' in request.GET:
        step = int(request.GET.get('step'))
        if 1 <= step <= total_steps:
            current_step = step
            request.session['profile_create_step'] = current_step
    
    # Initialize provider instance (may be draft)
    provider = None
    if hasattr(request.user, 'provider_profile'):
        provider = request.user.provider_profile
    else:
        # Check if there's a draft in session
        provider_id = request.session.get('draft_provider_id')
        if provider_id:
            try:
                provider = ServiceProvider.objects.get(id=provider_id, user=request.user, is_draft=True)
            except ServiceProvider.DoesNotExist:
                pass
    
    # Step 1: Basic Information
    if current_step == 1:
        if request.method == 'POST':
            form = ProviderBasicInfoForm(request.POST, instance=provider)
            if form.is_valid():
                provider = form.save(commit=False)
                if not provider.user:
                    provider.user = request.user
                if not provider.slug:
                    provider.slug = slugify(provider.name)
                    # Handle duplicate slugs
                    base_slug = provider.slug
                    counter = 1
                    while ServiceProvider.objects.filter(slug=provider.slug).exists():
                        provider.slug = f"{base_slug}-{counter}"
                        counter += 1
                provider.is_draft = True
                provider.approval_status = 'draft'
                provider.save()
                request.session['draft_provider_id'] = provider.id
                request.session['profile_create_step'] = 2
                messages.success(request, 'Basic information saved!')
                return redirect('providers:profile_create')
        else:
            form = ProviderBasicInfoForm(instance=provider)
        
        progress_percentage = provider.completion_percentage if provider else (current_step / total_steps * 100)
        return render(request, 'providers/profile/create_step1.html', {
            'form': form,
            'current_step': current_step,
            'total_steps': total_steps,
            'provider': provider,
            'progress_percentage': progress_percentage,
        })
    
    # Ensure we have a provider before proceeding to other steps
    if not provider:
        messages.warning(request, 'Please complete Step 1 first.')
        return redirect('providers:profile_create?step=1')
    
    # Step 2: Contact & Location
    if current_step == 2:
        if request.method == 'POST':
            form = ProviderContactLocationForm(request.POST, instance=provider, user=request.user)
            if form.is_valid():
                form.save()
                request.session['profile_create_step'] = 3
                messages.success(request, 'Contact information saved!')
                return redirect('providers:profile_create')
        else:
            form = ProviderContactLocationForm(instance=provider, user=request.user)
        
        progress_percentage = provider.completion_percentage if provider else (current_step / total_steps * 100)
        return render(request, 'providers/profile/create_step2.html', {
            'form': form,
            'current_step': current_step,
            'total_steps': total_steps,
            'provider': provider,
            'progress_percentage': progress_percentage,
        })
    
    # Step 3: Business Details
    if current_step == 3:
        if request.method == 'POST':
            form = ProviderBusinessDetailsForm(request.POST, instance=provider)
            # Handle business hours manually since we're using custom field names
            hours_instance = getattr(provider, 'business_hours', None)
            if hours_instance:
                hours_form = BusinessHoursForm(request.POST, instance=hours_instance)
            else:
                hours_form = BusinessHoursForm(request.POST)
            area_formset = ServiceAreaFormSet(request.POST, instance=provider)
            
            if form.is_valid() and hours_form.is_valid() and area_formset.is_valid():
                form.save()
                # Save business hours
                hours = hours_form.save(commit=False)
                hours.provider = provider
                hours.save()
                # Save service areas
                area_formset.save()
                request.session['profile_create_step'] = 4
                messages.success(request, 'Business details saved!')
                return redirect('providers:profile_create')
        else:
            form = ProviderBusinessDetailsForm(instance=provider)
            # Get or create business hours instance
            hours_instance, created = BusinessHours.objects.get_or_create(provider=provider)
            hours_form = BusinessHoursForm(instance=hours_instance)
            area_formset = ServiceAreaFormSet(instance=provider)
        
        progress_percentage = provider.completion_percentage if provider else (current_step / total_steps * 100)
        return render(request, 'providers/profile/create_step3.html', {
            'form': form,
            'hours_form': hours_form,
            'area_formset': area_formset,
            'current_step': current_step,
            'total_steps': total_steps,
            'provider': provider,
            'progress_percentage': progress_percentage,
        })
    
    # Step 4: Media & Portfolio
    if current_step == 4:
        if request.method == 'POST':
            form = ProviderMediaForm(request.POST, request.FILES, instance=provider)
            if form.is_valid():
                form.save()
                request.session['profile_create_step'] = 5
                messages.success(request, 'Media uploaded!')
                return redirect('providers:profile_create')
        else:
            form = ProviderMediaForm(instance=provider)
        
        progress_percentage = provider.completion_percentage if provider else (current_step / total_steps * 100)
        return render(request, 'providers/profile/create_step4.html', {
            'form': form,
            'current_step': current_step,
            'total_steps': total_steps,
            'provider': provider,
            'progress_percentage': progress_percentage,
        })
    
    # Step 5: Availability & Emergency
    if current_step == 5:
        if request.method == 'POST':
            form = ProviderAvailabilityForm(request.POST, instance=provider)
            if form.is_valid():
                form.save()
                # Check completion percentage
                completion = provider.completion_percentage
                if completion < 50:
                    messages.warning(
                        request,
                        f'Your profile is only {completion}% complete. '
                        'Please complete at least 50% to submit for review.'
                    )
                    return redirect('providers:profile_create?step=5')
                
                # Show preview/submit page
                return redirect('providers:profile_preview')
        else:
            form = ProviderAvailabilityForm(instance=provider)
        
        progress_percentage = provider.completion_percentage if provider else (current_step / total_steps * 100)
        return render(request, 'providers/profile/create_step5.html', {
            'form': form,
            'current_step': current_step,
            'total_steps': total_steps,
            'provider': provider,
            'completion_percentage': provider.completion_percentage,
            'progress_percentage': progress_percentage,
        })


@login_required
def provider_profile_preview(request):
    """Preview profile before submission."""
    try:
        provider = request.user.provider_profile
    except ServiceProvider.DoesNotExist:
        messages.error(request, 'No profile found. Please create one first.')
        return redirect('providers:join_as_pro')
    
    if request.method == 'POST' and 'submit_for_review' in request.POST:
        # Check completion
        if not provider.can_submit():
            messages.warning(
                request,
                f'Your profile is only {provider.completion_percentage}% complete. '
                'Please complete at least 50% to submit.'
            )
            return redirect('providers:profile_preview')
        
        # Activate profile immediately - no approval needed
        provider.is_draft = False
        provider.approval_status = 'approved'
        provider.is_active = True
        provider.approved_at = timezone.now()
        provider.submitted_for_review_at = timezone.now()
        provider.save()
        
        # Clear session data
        if 'draft_provider_id' in request.session:
            del request.session['draft_provider_id']
        if 'profile_create_step' in request.session:
            del request.session['profile_create_step']
        
        messages.success(
            request,
            f'Congratulations! Your provider profile "{provider.name}" is now live and visible to customers!'
        )
        return redirect('providers:profile_status')
    
    return render(request, 'providers/profile/preview.html', {
        'provider': provider,
        'completion_percentage': provider.completion_percentage,
    })


# Email verification removed - profiles are approved immediately upon submission


@login_required
def provider_profile_status(request):
    """View provider profile status."""
    try:
        provider = request.user.provider_profile
    except ServiceProvider.DoesNotExist:
        messages.info(request, 'You do not have a provider profile yet.')
        return redirect('providers:join_as_pro')
    
    return render(request, 'providers/profile/status.html', {
        'provider': provider,
        'completion_percentage': provider.completion_percentage,
    })


class ProviderProfileEditView(LoginRequiredMixin, UpdateView):
    """Edit existing provider profile."""
    
    model = ServiceProvider
    template_name = 'providers/profile/edit.html'
    fields = [
        'name', 'category', 'tagline', 'description', 'skills',
        'email', 'phone', 'website', 'address', 'city', 'state', 'zip_code',
        'pricing_range', 'years_experience',
        'logo', 'image',
        'accepts_emergency', 'emergency_rate_info', 'is_available_now',
    ]
    
    def get_object(self):
        return get_object_or_404(ServiceProvider, user=self.request.user)
    
    def get_success_url(self):
        messages.success(self.request, 'Profile updated successfully!')
        return reverse('providers:profile_status')
    
    def get_form_class(self):
        # Return a combined form or use ModelForm
        from django import forms
        from django.forms import ModelForm
        class ProviderEditForm(ModelForm):
            class Meta:
                model = ServiceProvider
                fields = self.fields
                widgets = {
                    'name': forms.TextInput(attrs={'class': 'input'}),
                    'category': forms.Select(attrs={'class': 'input'}),
                    'tagline': forms.TextInput(attrs={'class': 'input'}),
                    'description': forms.Textarea(attrs={'class': 'input', 'rows': 5}),
                    'skills': forms.Textarea(attrs={'class': 'input', 'rows': 3}),
                    'email': forms.EmailInput(attrs={'class': 'input'}),
                    'phone': forms.TextInput(attrs={'class': 'input'}),
                    'website': forms.URLInput(attrs={'class': 'input'}),
                    'address': forms.TextInput(attrs={'class': 'input'}),
                    'city': forms.TextInput(attrs={'class': 'input'}),
                    'state': forms.TextInput(attrs={'class': 'input'}),
                    'zip_code': forms.TextInput(attrs={'class': 'input'}),
                    'pricing_range': forms.Select(attrs={'class': 'input'}),
                    'years_experience': forms.NumberInput(attrs={'class': 'input'}),
                    'logo': forms.FileInput(attrs={'class': 'input'}),
                    'image': forms.FileInput(attrs={'class': 'input'}),
                    'accepts_emergency': forms.CheckboxInput(attrs={'class': 'checkbox'}),
                    'emergency_rate_info': forms.TextInput(attrs={'class': 'input'}),
                    'is_available_now': forms.CheckboxInput(attrs={'class': 'checkbox'}),
                }
        return ProviderEditForm

