"""
Views for credit dashboard and management.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import CustomUser
from .modes_models import SkillCredit, SkillSwapJob
from .credit_service import CreditTransactionService


class CreditDashboardView(LoginRequiredMixin, ListView):
    """Credit dashboard with balance, history, and statistics."""
    
    model = SkillCredit
    template_name = 'accounts/credits/dashboard.html'
    context_object_name = 'transactions'
    paginate_by = 25
    
    def get_queryset(self):
        """Get user's credit transactions."""
        return CreditTransactionService.get_transaction_history(
            self.request.user,
            limit=100
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get credit summary
        summary = CreditTransactionService.get_credits_summary(user, days=30)
        context.update(summary)
        
        # Get pending jobs
        pending_jobs = SkillSwapJob.objects.filter(
            Q(requester=user) | Q(provider=user),
            status__in=['accepted', 'in_progress']
        ).select_related('requester', 'provider', 'skill_needed')
        context['pending_jobs'] = pending_jobs
        
        # Get transaction statistics for chart
        transactions = CreditTransactionService.get_transaction_history(user, limit=100)
        
        # Group by date for chart
        chart_data = {}
        for trans in transactions:
            date_key = trans.created_at.date().isoformat()
            if date_key not in chart_data:
                chart_data[date_key] = {'earned': Decimal('0'), 'spent': Decimal('0')}
            
            if trans.transaction_type in ['earned', 'bonus', 'refund']:
                chart_data[date_key]['earned'] += trans.credits
            elif trans.transaction_type in ['spent', 'escrow_hold']:
                chart_data[date_key]['spent'] += trans.credits
        
        context['chart_data'] = sorted(chart_data.items())
        
        # Filter options
        context['transaction_type'] = self.request.GET.get('type', 'all')
        if context['transaction_type'] != 'all':
            context['transactions'] = context['transactions'].filter(
                transaction_type=context['transaction_type']
            )
        
        return context


class CreditTransactionDetailView(LoginRequiredMixin, DetailView):
    """View details of a specific credit transaction."""
    
    model = SkillCredit
    template_name = 'accounts/credits/transaction_detail.html'
    context_object_name = 'transaction'
    
    def get_queryset(self):
        """User can only view their own transactions."""
        return SkillCredit.objects.filter(
            Q(to_user=self.request.user) | Q(from_user=self.request.user)
        ).select_related('from_user', 'to_user', 'job', 'skill_swapped', 'verified_by')


@login_required
def credit_transaction_history(request):
    """Filtered transaction history view."""
    user = request.user
    transaction_type = request.GET.get('type', 'all')
    days = int(request.GET.get('days', 30))
    
    transactions = CreditTransactionService.get_transaction_history(user)
    
    if transaction_type != 'all':
        transactions = transactions.filter(transaction_type=transaction_type)
    
    # Filter by date range
    if days:
        cutoff_date = timezone.now() - timedelta(days=days)
        transactions = transactions.filter(created_at__gte=cutoff_date)
    
    context = {
        'transactions': transactions,
        'transaction_type': transaction_type,
        'days': days,
        'summary': CreditTransactionService.get_credits_summary(user, days=days),
    }
    
    return render(request, 'accounts/credits/history.html', context)


@login_required
def confirm_job_completion(request, job_id):
    """Confirm job completion to release escrow."""
    job = get_object_or_404(
        SkillSwapJob.objects.filter(
            Q(requester=request.user) | Q(provider=request.user)
        ),
        pk=job_id
    )
    
    if request.method == 'POST':
        if request.user == job.requester:
            job.requester_confirmed = True
        elif request.user == job.provider:
            job.provider_confirmed = True
        
        # If both confirmed, mark as completed
        if job.requester_confirmed and job.provider_confirmed:
            job.status = 'completed'
            job.completed_at = timezone.now()
            
            # Release escrow
            success, error = CreditTransactionService.release_escrow(job)
            if success:
                messages.success(request, 'Job completed! Credits have been transferred.')
            else:
                messages.error(request, f'Error releasing credits: {error}')
        else:
            messages.info(request, 'Completion confirmed. Waiting for other party to confirm.')
        
        job.save()
        return redirect('accounts:credit_dashboard')
    
    context = {
        'job': job,
        'is_requester': request.user == job.requester,
    }
    return render(request, 'accounts/credits/confirm_completion.html', context)
