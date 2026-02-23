"""
Views for multi-mode profile system.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import CustomUser
from .modes_models import (
    Skill, FreelanceListing, FreelancePortfolioItem,
    SkillSwapListing, SkillCredit
)
from .modes_forms import (
    FreelanceListingForm, FreelancePortfolioItemFormSet,
    SkillSwapListingForm, SkillCreditForm, ProfileModeToggleForm
)


# ============================================================================
# Mode Management Views
# ============================================================================

class ProfileModesView(LoginRequiredMixin, TemplateView):
    """Dashboard for managing all profile modes."""
    
    template_name = 'accounts/modes/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        context['user'] = user
        context['has_provider'] = user.has_provider_profile
        context['has_freelance'] = user.has_freelance_listing
        context['has_skill_swap'] = user.has_skill_swap_listing
        context['active_modes'] = user.active_modes
        context['active_mode'] = user.active_mode
        
        # Get listings if they exist
        if user.has_freelance_listing:
            context['freelance_listing'] = user.freelance_listing
        if user.has_skill_swap_listing:
            context['skill_swap_listing'] = user.skill_swap_listing
            context['credits_balance'] = user.skill_swap_listing.credits_balance
        else:
            context['credits_balance'] = 0
        
        return context


@login_required
@require_POST
def toggle_profile_mode(request):
    """Toggle profile mode activation."""
    user = request.user
    mode = request.POST.get('mode')
    enable = request.POST.get('enable') == 'true'
    
    if mode == 'freelance':
        if enable:
            # Check if listing exists, if not redirect to create
            if not user.has_freelance_listing:
                messages.info(request, 'Please create a freelance listing first.')
                return redirect('accounts:freelance_create')
            user.is_freelancer_active = True
        else:
            user.is_freelancer_active = False
        user.save()
        messages.success(request, f'Freelance mode {"activated" if enable else "deactivated"}.')
    
    elif mode == 'skill_swap':
        if enable:
            # Check if listing exists, if not redirect to create
            if not user.has_skill_swap_listing:
                messages.info(request, 'Please create a skill swap listing first.')
                return redirect('accounts:skill_swap_create')
            user.is_skill_swap_active = True
        else:
            user.is_skill_swap_active = False
        user.save()
        messages.success(request, f'Skill swap mode {"activated" if enable else "deactivated"}.')
    
    return redirect('accounts:modes_dashboard')


@login_required
@require_POST
def set_active_mode(request):
    """Set the active mode for UI context."""
    user = request.user
    mode = request.POST.get('mode')
    
    if mode in ['provider', 'freelance', 'skill_swap']:
        # Verify user has access to this mode
        if mode == 'provider' and not user.has_provider_profile:
            messages.error(request, 'You need to create a provider profile first.')
            return redirect('accounts:modes_dashboard')
        elif mode == 'freelance' and not user.has_freelance_listing:
            messages.error(request, 'You need to create a freelance listing first.')
            return redirect('accounts:modes_dashboard')
        elif mode == 'skill_swap' and not user.has_skill_swap_listing:
            messages.error(request, 'You need to create a skill swap listing first.')
            return redirect('accounts:modes_dashboard')
        
        user.active_mode = mode
        user.save()
        messages.success(request, f'Switched to {mode.replace("_", " ").title()} mode.')
    
    return redirect('accounts:modes_dashboard')


# ============================================================================
# Freelance Listing Views
# ============================================================================

class FreelanceListingCreateView(LoginRequiredMixin, CreateView):
    """Create a freelance listing."""
    
    model = FreelanceListing
    form_class = FreelanceListingForm
    template_name = 'accounts/modes/freelance_form.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.is_active = True
        response = super().form_valid(form)
        # Auto-activate freelance mode
        self.request.user.is_freelancer_active = True
        self.request.user.save()
        messages.success(self.request, 'Freelance listing created! Your freelance mode is now active.')
        return response
    
    def get_success_url(self):
        return reverse('accounts:freelance_detail', kwargs={'pk': self.object.pk})


class FreelanceListingUpdateView(LoginRequiredMixin, UpdateView):
    """Update a freelance listing."""
    
    model = FreelanceListing
    form_class = FreelanceListingForm
    template_name = 'accounts/modes/freelance_form.html'
    
    def get_queryset(self):
        return FreelanceListing.objects.filter(user=self.request.user)
    
    def get_success_url(self):
        messages.success(self.request, 'Freelance listing updated!')
        return reverse('accounts:freelance_detail', kwargs={'pk': self.object.pk})


class FreelanceListingDetailView(DetailView):
    """View a freelance listing."""
    
    model = FreelanceListing
    template_name = 'accounts/modes/freelance_detail.html'
    context_object_name = 'listing'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['portfolio_items'] = self.object.portfolio_items.all()
        return context


class FreelanceListingListView(ListView):
    """List all active freelance listings."""
    
    model = FreelanceListing
    template_name = 'accounts/modes/freelance_list.html'
    context_object_name = 'listings'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = FreelanceListing.objects.filter(is_active=True).select_related('user')
        
        # Search
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(bio__icontains=query) |
                Q(expertise_tags__icontains=query)
            )
        
        # Filter by skill
        skill = self.request.GET.get('skill', '').strip()
        if skill:
            queryset = queryset.filter(skills__slug=skill)
        
        # Filter by pricing type
        pricing_type = self.request.GET.get('pricing_type', '').strip()
        if pricing_type:
            queryset = queryset.filter(pricing_type=pricing_type)
        
        return queryset.distinct()


@login_required
def freelance_portfolio_manage(request, pk):
    """Manage portfolio items for a freelance listing."""
    listing = get_object_or_404(FreelanceListing, pk=pk, user=request.user)
    
    if request.method == 'POST':
        formset = FreelancePortfolioItemFormSet(request.POST, request.FILES, instance=listing)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Portfolio updated!')
            return redirect('accounts:freelance_detail', pk=listing.pk)
    else:
        formset = FreelancePortfolioItemFormSet(instance=listing)
    
    return render(request, 'accounts/modes/freelance_portfolio.html', {
        'listing': listing,
        'formset': formset,
    })


# ============================================================================
# Skill Swap Listing Views
# ============================================================================

class SkillSwapListingCreateView(LoginRequiredMixin, CreateView):
    """Create a skill swap listing."""
    
    model = SkillSwapListing
    form_class = SkillSwapListingForm
    template_name = 'accounts/modes/skill_swap_form.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.is_active = True
        response = super().form_valid(form)
        # Auto-activate skill swap mode
        self.request.user.is_skill_swap_active = True
        self.request.user.save()
        messages.success(self.request, 'Skill swap listing created! Your skill swap mode is now active.')
        return response
    
    def get_success_url(self):
        return reverse('accounts:skill_swap_detail', kwargs={'pk': self.object.pk})


class SkillSwapListingUpdateView(LoginRequiredMixin, UpdateView):
    """Update a skill swap listing."""
    
    model = SkillSwapListing
    form_class = SkillSwapListingForm
    template_name = 'accounts/modes/skill_swap_form.html'
    
    def get_queryset(self):
        return SkillSwapListing.objects.filter(user=self.request.user)
    
    def get_success_url(self):
        messages.success(self.request, 'Skill swap listing updated!')
        return reverse('accounts:skill_swap_detail', kwargs={'pk': self.object.pk})


class SkillSwapListingDetailView(DetailView):
    """View a skill swap listing."""
    
    model = SkillSwapListing
    template_name = 'accounts/modes/skill_swap_detail.html'
    context_object_name = 'listing'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['credits_balance'] = self.object.credits_balance
        context['recent_credits'] = SkillCredit.objects.filter(
            Q(from_user=self.object.user) | Q(to_user=self.object.user),
            status='approved'
        ).order_by('-swap_date')[:10]
        return context


class SkillSwapListingListView(ListView):
    """List all active skill swap listings."""
    
    model = SkillSwapListing
    template_name = 'accounts/modes/skill_swap_list.html'
    context_object_name = 'listings'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = SkillSwapListing.objects.filter(is_active=True).select_related('user')
        
        # Search
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(bio__icontains=query) |
                Q(additional_skills_offered__icontains=query) |
                Q(additional_skills_wanted__icontains=query)
            )
        
        # Filter by skill offered
        skill_offered = self.request.GET.get('skill_offered', '').strip()
        if skill_offered:
            queryset = queryset.filter(skills_offered__slug=skill_offered)
        
        # Filter by skill wanted
        skill_wanted = self.request.GET.get('skill_wanted', '').strip()
        if skill_wanted:
            queryset = queryset.filter(skills_wanted__slug=skill_wanted)
        
        # Filter by location
        location = self.request.GET.get('location', '').strip()
        if location:
            queryset = queryset.filter(
                Q(location_preference__icontains=location) |
                Q(accepts_remote=True)
            )
        
        return queryset.distinct()


# ============================================================================
# Skill Credit Views
# ============================================================================

@login_required
def skill_credit_create(request):
    """Create a skill credit transaction."""
    if request.method == 'POST':
        form = SkillCreditForm(request.POST, user=request.user)
        if form.is_valid():
            credit = form.save(commit=False)
            credit.from_user = request.user
            credit.status = 'pending'  # Requires approval
            credit.save()
            messages.success(
                request,
                f'Credit transaction submitted for approval. '
                f'{credit.to_user.full_name} will be notified.'
            )
            return redirect('accounts:skill_credits')
    else:
        form = SkillCreditForm(user=request.user)
    
    return render(request, 'accounts/modes/skill_credit_form.html', {
        'form': form,
    })


@login_required
def skill_credits_list(request):
    """List user's skill credit transactions."""
    credits_given = SkillCredit.objects.filter(from_user=request.user).order_by('-created_at')
    credits_received = SkillCredit.objects.filter(to_user=request.user).order_by('-created_at')
    
    return render(request, 'accounts/modes/skill_credits.html', {
        'credits_given': credits_given,
        'credits_received': credits_received,
    })


@login_required
@require_POST
def approve_skill_credit(request, pk):
    """Approve a skill credit transaction."""
    credit = get_object_or_404(
        SkillCredit,
        pk=pk,
        to_user=request.user,
        status='pending'
    )
    
    credit.status = 'approved'
    credit.verified_by = request.user
    from django.utils import timezone
    credit.verified_at = timezone.now()
    credit.save()
    
    messages.success(request, 'Credit transaction approved!')
    return redirect('accounts:skill_credits')


# ============================================================================
# Skill Views
# ============================================================================

class SkillListView(ListView):
    """List all skills."""
    
    model = Skill
    template_name = 'accounts/modes/skill_list.html'
    context_object_name = 'skills'
    
    def get_queryset(self):
        return Skill.objects.filter(is_active=True)


class SkillDetailView(DetailView):
    """View skill details."""
    
    model = Skill
    template_name = 'accounts/modes/skill_detail.html'
    context_object_name = 'skill'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['freelance_listings'] = self.object.freelance_listings.filter(is_active=True)[:5]
        context['swap_listings_offered'] = self.object.swap_listings_offered.filter(is_active=True)[:5]
        context['swap_listings_wanted'] = self.object.swap_listings_wanted.filter(is_active=True)[:5]
        return context
