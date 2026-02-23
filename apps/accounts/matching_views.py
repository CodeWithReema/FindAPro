"""
Views for smart matching system.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, TemplateView
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q

from .models import CustomUser
from .matching_models import Match, MatchHistory
from .matching_service import MatchingService


class MatchSuggestionsView(LoginRequiredMixin, TemplateView):
    """View showing match suggestions for the user."""
    
    template_name = 'accounts/matching/suggestions.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        matching_service = MatchingService(user)
        
        # Get filter type
        match_type = self.request.GET.get('type', 'all')
        
        # Get matches based on type
        skill_swap_matches = []
        freelance_matches = []
        
        if match_type in ['all', 'skill_swap']:
            try:
                skill_swap_matches = matching_service.find_skill_swap_matches(limit=10, min_score=30)
            except Exception:
                skill_swap_matches = []
        
        if match_type in ['all', 'freelance']:
            try:
                freelance_matches = matching_service.find_freelance_collab_matches(limit=10, min_score=30)
            except Exception:
                freelance_matches = []
        
        # Combine and sort all matches
        all_matches = list(skill_swap_matches) + list(freelance_matches)
        all_matches.sort(key=lambda x: x.compatibility_score, reverse=True)
        
        context['skill_swap_matches'] = skill_swap_matches[:10]
        context['freelance_matches'] = freelance_matches[:10]
        context['all_matches'] = all_matches[:10]
        context['match_type'] = match_type
        context['new_matches_count'] = matching_service.get_new_matches_count(days=7)
        
        return context


class MatchDetailView(LoginRequiredMixin, DetailView):
    """View details of a specific match."""
    
    model = Match
    template_name = 'accounts/matching/match_detail.html'
    context_object_name = 'match'
    
    def get_queryset(self):
        # User can only view matches they're involved in
        return Match.objects.filter(
            Q(user_a=self.request.user) | Q(user_b=self.request.user)
        ).select_related('user_a', 'user_b')
    
    def get_object(self):
        match = super().get_object()
        # Mark as viewed
        match.mark_viewed(self.request.user)
        return match
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        match = self.object
        
        # Determine which user is the "other" user
        if match.user_a == self.request.user:
            context['other_user'] = match.user_b
            context['is_user_a'] = True
            context['user'] = match.user_a
        else:
            context['other_user'] = match.user_a
            context['is_user_a'] = False
            context['user'] = match.user_b
        
        # Get user's listings
        if match.match_type == 'skill_swap':
            if hasattr(context['user'], 'skill_swap_listing'):
                context['user_a_listing'] = context['user'].skill_swap_listing
            if hasattr(context['other_user'], 'skill_swap_listing'):
                context['user_b_listing'] = context['other_user'].skill_swap_listing
        elif match.match_type == 'freelance_collab':
            if hasattr(context['user'], 'freelance_listing'):
                context['user_a_listing'] = context['user'].freelance_listing
            if hasattr(context['other_user'], 'freelance_listing'):
                context['user_b_listing'] = context['other_user'].freelance_listing
        
        return context


class MyMatchesView(LoginRequiredMixin, ListView):
    """View user's match history and connections."""
    
    model = Match
    template_name = 'accounts/matching/my_matches.html'
    context_object_name = 'matches'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Match.objects.filter(
            Q(user_a=self.request.user) | Q(user_b=self.request.user)
        ).select_related('user_a', 'user_b')
        
        # Filter by status
        status_filter = self.request.GET.get('status', 'all')
        if status_filter != 'all':
            queryset = queryset.filter(status=status_filter)
        
        # Filter by type
        type_filter = self.request.GET.get('type', 'all')
        if type_filter != 'all':
            queryset = queryset.filter(match_type=type_filter)
        
        return queryset.order_by('-compatibility_score', '-created_at')


@login_required
@require_POST
def mark_match_interested(request, pk):
    """Mark user as interested in a match."""
    match = get_object_or_404(
        Match.objects.filter(
            Q(user_a=request.user) | Q(user_b=request.user)
        ),
        pk=pk
    )
    
    match.mark_interested(request.user)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'is_mutual': match.is_mutual_interest,
            'status': match.status,
            'message': 'Match marked as interested!' if not match.is_mutual_interest else 'Connection made! Both users are interested.'
        })
    
    messages.success(request, 'Match marked as interested!')
    return redirect('accounts:match_detail', pk=match.pk)


@login_required
@require_POST
def mark_match_not_interested(request, pk):
    """Mark user as not interested in a match."""
    match = get_object_or_404(
        Match.objects.filter(
            Q(user_a=request.user) | Q(user_b=request.user)
        ),
        pk=pk
    )
    
    match.mark_not_interested(request.user)
    
    # Record in history
    MatchHistory.objects.create(
        user=request.user,
        matched_user=match.user_b if match.user_a == request.user else match.user_a,
        match=match,
        action='not_interested'
    )
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Match hidden. You won\'t see this suggestion again.'
        })
    
    messages.info(request, 'Match hidden. You won\'t see this suggestion again.')
    return redirect('accounts:match_suggestions')


@login_required
def refresh_matches(request):
    """Refresh/regenerate matches for the user."""
    matching_service = MatchingService(request.user)
    
    # Generate new matches
    skill_swap_matches = matching_service.find_skill_swap_matches(limit=20, min_score=30)
    freelance_matches = matching_service.find_freelance_collab_matches(limit=20, min_score=30)
    
    total_new = len(skill_swap_matches) + len(freelance_matches)
    
    messages.success(request, f'Found {total_new} new potential matches!')
    return redirect('accounts:match_suggestions')
