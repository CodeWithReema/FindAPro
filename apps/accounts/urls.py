"""
URL patterns for accounts app.
"""

from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views
from . import modes_views
from . import matching_views
from . import credit_views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('dashboard/', login_required(views.UserDashboardView.as_view()), name='dashboard'),
    path('profile/edit/', views.profile_update_view, name='profile_edit'),
    
    # Profile Modes Management
    path('modes/', login_required(modes_views.ProfileModesView.as_view()), name='modes_dashboard'),
    path('modes/toggle/', login_required(modes_views.toggle_profile_mode), name='toggle_mode'),
    path('modes/set-active/', login_required(modes_views.set_active_mode), name='set_active_mode'),
    
    # Freelance Listings
    path('freelance/', modes_views.FreelanceListingListView.as_view(), name='freelance_list'),
    path('freelance/create/', login_required(modes_views.FreelanceListingCreateView.as_view()), name='freelance_create'),
    path('freelance/<int:pk>/', modes_views.FreelanceListingDetailView.as_view(), name='freelance_detail'),
    path('freelance/<int:pk>/edit/', login_required(modes_views.FreelanceListingUpdateView.as_view()), name='freelance_edit'),
    path('freelance/<int:pk>/portfolio/', login_required(modes_views.freelance_portfolio_manage), name='freelance_portfolio'),
    
    # Skill Swap Listings
    path('skill-swap/', modes_views.SkillSwapListingListView.as_view(), name='skill_swap_list'),
    path('skill-swap/create/', login_required(modes_views.SkillSwapListingCreateView.as_view()), name='skill_swap_create'),
    path('skill-swap/<int:pk>/', modes_views.SkillSwapListingDetailView.as_view(), name='skill_swap_detail'),
    path('skill-swap/<int:pk>/edit/', login_required(modes_views.SkillSwapListingUpdateView.as_view()), name='skill_swap_edit'),
    
    # Skill Credits (Legacy)
    path('credits/', login_required(modes_views.skill_credits_list), name='skill_credits'),
    path('credits/create/', login_required(modes_views.skill_credit_create), name='skill_credit_create'),
    path('credits/<int:pk>/approve/', login_required(modes_views.approve_skill_credit), name='skill_credit_approve'),
    
    # Credit Dashboard (New)
    path('credits/dashboard/', login_required(credit_views.CreditDashboardView.as_view()), name='credit_dashboard'),
    path('credits/history/', login_required(credit_views.credit_transaction_history), name='credit_history'),
    path('credits/transaction/<int:pk>/', login_required(credit_views.CreditTransactionDetailView.as_view()), name='credit_transaction_detail'),
    path('credits/job/<int:job_id>/confirm/', login_required(credit_views.confirm_job_completion), name='confirm_job_completion'),
    
    # Skills
    path('skills/', modes_views.SkillListView.as_view(), name='skill_list'),
    path('skills/<slug:slug>/', modes_views.SkillDetailView.as_view(), name='skill_detail'),
    
    # Smart Matching
    path('matches/', login_required(matching_views.MatchSuggestionsView.as_view()), name='match_suggestions'),
    path('matches/my-matches/', login_required(matching_views.MyMatchesView.as_view()), name='my_matches'),
    path('matches/<int:pk>/', login_required(matching_views.MatchDetailView.as_view()), name='match_detail'),
    path('matches/<int:pk>/interested/', login_required(matching_views.mark_match_interested), name='match_interested'),
    path('matches/<int:pk>/not-interested/', login_required(matching_views.mark_match_not_interested), name='match_not_interested'),
    path('matches/refresh/', login_required(matching_views.refresh_matches), name='refresh_matches'),
]

