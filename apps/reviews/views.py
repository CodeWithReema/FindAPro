"""
Views for reviews app - Template views.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import ProviderReview
from .forms import ReviewForm
from apps.providers.models import ServiceProvider


@login_required
def create_review(request, provider_slug):
    """Create a new review for a provider."""
    provider = get_object_or_404(ServiceProvider, slug=provider_slug, is_active=True)
    
    # Check if user already reviewed
    existing_review = ProviderReview.objects.filter(
        user=request.user,
        provider=provider
    ).first()
    
    if existing_review:
        messages.warning(request, 'You have already reviewed this provider. You can edit your review below.')
        return redirect('reviews:edit_review', review_id=existing_review.id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.provider = provider
            review.save()
            messages.success(request, 'Your review has been submitted!')
            return redirect('providers:provider_detail', slug=provider.slug)
    else:
        form = ReviewForm()
    
    return render(request, 'reviews/create_review.html', {
        'form': form,
        'provider': provider
    })


@login_required
def edit_review(request, review_id):
    """Edit an existing review."""
    review = get_object_or_404(ProviderReview, id=review_id, user=request.user)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your review has been updated!')
            return redirect('providers:provider_detail', slug=review.provider.slug)
    else:
        form = ReviewForm(instance=review)
    
    return render(request, 'reviews/edit_review.html', {
        'form': form,
        'review': review,
        'provider': review.provider
    })


@login_required
def delete_review(request, review_id):
    """Delete a review."""
    review = get_object_or_404(ProviderReview, id=review_id, user=request.user)
    provider_slug = review.provider.slug
    
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Your review has been deleted.')
        return redirect('providers:provider_detail', slug=provider_slug)
    
    return render(request, 'reviews/delete_review.html', {
        'review': review
    })


@require_POST
@login_required
def mark_helpful(request, review_id):
    """Mark a review as helpful (AJAX)."""
    review = get_object_or_404(ProviderReview, id=review_id)
    
    # Simple increment (in production, track which users marked helpful)
    review.helpful_count += 1
    review.save()
    
    return JsonResponse({
        'success': True,
        'helpful_count': review.helpful_count
    })

