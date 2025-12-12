"""
Views for providers app - Template views.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Avg, Count
from django.utils import timezone
from django.urls import reverse

from .models import ServiceCategory, ServiceProvider, FavoriteProvider, QuoteRequest
from .forms import QuoteRequestForm, QuoteResponseForm, MatchingQuizForm


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

