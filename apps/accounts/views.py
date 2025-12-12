"""
Views for user authentication and profile management.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, TemplateView
from django.urls import reverse_lazy

from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm


class RegisterView(CreateView):
    """User registration view."""
    
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('core:home')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, f'Welcome to FindAPro, {self.object.first_name}!')
        return response
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:home')
        return super().dispatch(request, *args, **kwargs)


class CustomLoginView(LoginView):
    """Custom login view with styled form."""
    
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().first_name or form.get_user().username}!')
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    """Custom logout view."""
    
    next_page = reverse_lazy('core:home')
    
    def dispatch(self, request, *args, **kwargs):
        messages.info(request, 'You have been logged out.')
        return super().dispatch(request, *args, **kwargs)


class UserDashboardView(TemplateView):
    """User dashboard view."""
    
    template_name = 'accounts/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user's reviews
        context['user_reviews'] = user.reviews.select_related('provider').order_by('-created_at')[:5]
        
        # If user is a provider, get their provider profile
        if user.is_provider and hasattr(user, 'provider_profile'):
            context['provider_profile'] = user.provider_profile
            context['provider_reviews'] = user.provider_profile.reviews.select_related('user').order_by('-created_at')[:5]
        
        return context


@login_required
def profile_update_view(request):
    """Update user profile view."""
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:dashboard')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile_edit.html', {'form': form})

