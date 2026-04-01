from django.urls import path
from . import views

app_name = 'bcubed'

urlpatterns = [
    path('', views.HubView.as_view(), name='hub'),
    path('build/', views.BuildView.as_view(), name='build'),
    path('brand/', views.BrandView.as_view(), name='brand'),
    path('bank/', views.BankView.as_view(), name='bank'),
    # AI API endpoints
    path('api/pitch/', views.api_pitch, name='api_pitch'),
    path('api/checklist/', views.api_checklist, name='api_checklist'),
    path('api/niche/', views.api_niche, name='api_niche'),
    path('api/names/', views.api_names, name='api_names'),
    path('api/tagline/', views.api_tagline, name='api_tagline'),
    path('api/copy/', views.api_copy, name='api_copy'),
    path('api/logo/', views.api_logo, name='api_logo'),
    path('api/seo/', views.api_seo, name='api_seo'),
    path('api/pricing/', views.api_pricing, name='api_pricing'),
    path('api/budget/', views.api_budget, name='api_budget'),
    path('api/tax/', views.api_tax, name='api_tax'),
    path('api/invoice/', views.api_invoice, name='api_invoice'),
    path('api/result/<int:pk>/delete/', views.delete_result, name='delete_result'),
    path('api/export-docx/', views.export_docx, name='export_docx'),
]
