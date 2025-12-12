"""
URL patterns for providers app - Template views.
"""

from django.urls import path
from . import views

app_name = 'providers'

urlpatterns = [
    path('', views.ProviderSearchView.as_view(), name='search'),
    path('match/', views.smart_match_quiz, name='smart_match'),
    path('emergency/', views.emergency_mode, name='emergency'),
    path('compare/', views.compare_providers, name='compare'),
    path('favorites/', views.FavoriteListView.as_view(), name='favorites'),
    path('favorite/<int:provider_id>/', views.toggle_favorite, name='toggle_favorite'),
    
    # Quote requests
    path('quotes/', views.MyQuotesView.as_view(), name='my_quotes'),
    path('quotes/received/', views.ProviderQuotesView.as_view(), name='provider_quotes'),
    path('quotes/<int:pk>/', views.quote_detail, name='quote_detail'),
    path('quotes/<int:pk>/<str:status>/', views.update_quote_status, name='update_quote_status'),
    path('<slug:slug>/request-quote/', views.QuoteRequestCreateView.as_view(), name='request_quote'),
    
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('<slug:slug>/', views.ProviderDetailView.as_view(), name='provider_detail'),
]

