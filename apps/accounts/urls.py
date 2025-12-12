"""
URL patterns for accounts app.
"""

from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('dashboard/', login_required(views.UserDashboardView.as_view()), name='dashboard'),
    path('profile/edit/', views.profile_update_view, name='profile_edit'),
]

