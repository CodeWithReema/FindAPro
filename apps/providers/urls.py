"""
URL patterns for providers app - Template views.
"""

from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views
from . import unified_job_views
from . import analytics_views
from . import project_views

app_name = 'providers'

urlpatterns = [
    path('', views.ProviderSearchView.as_view(), name='search'),
    path('match/', views.smart_match_quiz, name='smart_match'),
    path('emergency/', views.emergency_mode, name='emergency'),
    path('compare/', views.compare_providers, name='compare'),
    path('favorites/', views.FavoriteListView.as_view(), name='favorites'),
    path('favorite/<int:provider_id>/', views.toggle_favorite, name='toggle_favorite'),
    
    # Provider profile creation and management
    path('join/', views.JoinAsProView.as_view(), name='join_as_pro'),
    path('profile/create/', views.provider_profile_create, name='profile_create'),
    path('profile/preview/', views.provider_profile_preview, name='profile_preview'),
    path('profile/status/', views.provider_profile_status, name='profile_status'),
    path('profile/edit/', views.ProviderProfileEditView.as_view(), name='profile_edit'),
    
    # Quote requests
    path('quotes/', views.MyQuotesView.as_view(), name='my_quotes'),
    path('quotes/received/', views.ProviderQuotesView.as_view(), name='provider_quotes'),
    path('quotes/<int:pk>/', views.quote_detail, name='quote_detail'),
    path('quotes/<int:pk>/<str:status>/', views.update_quote_status, name='update_quote_status'),
    path('<slug:slug>/request-quote/', views.QuoteRequestCreateView.as_view(), name='request_quote'),
    
    # Unified Job System
    path('jobs/', login_required(unified_job_views.UnifiedJobListView.as_view()), name='unified_job_dashboard'),
    path('jobs/create/provider/<slug:slug>/', login_required(unified_job_views.UnifiedJobCreateView.as_view()), name='unified_job_create_provider'),
    path('jobs/create/user/<int:user_id>/', login_required(unified_job_views.UnifiedJobCreateView.as_view()), name='unified_job_create_user'),
    path('jobs/<int:pk>/', login_required(unified_job_views.UnifiedJobDetailView.as_view()), name='unified_job_detail'),
    path('jobs/<int:job_id>/proposal/', login_required(unified_job_views.submit_job_proposal), name='submit_job_proposal'),
    path('jobs/<int:job_id>/message/', login_required(unified_job_views.send_job_message), name='send_job_message'),
    path('jobs/<int:job_id>/confirm/', login_required(unified_job_views.confirm_job_completion), name='confirm_unified_job_completion'),
    path('proposals/<int:proposal_id>/<str:action>/', login_required(unified_job_views.respond_to_proposal), name='respond_to_proposal'),
    
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    
    # Skill Analytics
    path('analytics/', login_required(analytics_views.SkillAnalyticsDashboardView.as_view()), name='skill_analytics_dashboard'),
    
    # Community Projects
    path('projects/', project_views.ProjectListView.as_view(), name='project_list'),
    path('projects/create/', login_required(project_views.ProjectCreateView.as_view()), name='project_create'),
    path('projects/<int:pk>/', project_views.ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<int:pk>/manage/', login_required(project_views.ProjectManageView.as_view()), name='project_manage'),
    path('projects/<int:project_id>/publish/', login_required(project_views.publish_project), name='publish_project'),
    path('applications/<int:application_id>/<str:action>/', login_required(project_views.review_application), name='review_application'),
    path('projects/<int:project_id>/milestone/', login_required(project_views.create_milestone), name='create_milestone'),
    path('projects/<int:project_id>/message/', login_required(project_views.send_project_message), name='send_project_message'),
    
    path('<slug:slug>/', views.ProviderDetailView.as_view(), name='provider_detail'),
]

