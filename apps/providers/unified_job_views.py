"""
Views for unified job/booking system.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse

from .models import ServiceProvider
from .unified_jobs import UnifiedJob, JobProposal, JobMessage
from .unified_job_forms import UnifiedJobRequestForm, JobProposalForm, JobMessageForm
from apps.accounts.credit_service import CreditTransactionService
from apps.accounts.modes_models import SkillSwapJob


class UnifiedJobCreateView(LoginRequiredMixin, CreateView):
    """Create a unified job request (paid, credit, or barter)."""
    
    model = UnifiedJob
    form_class = UnifiedJobRequestForm
    template_name = 'providers/jobs/unified_job_form.html'
    
    def get_provider(self):
        """Get provider from slug or user."""
        slug = self.kwargs.get('slug')
        if slug:
            return get_object_or_404(ServiceProvider, slug=slug, is_active=True)
        user_id = self.kwargs.get('user_id')
        if user_id:
            from apps.accounts.models import CustomUser
            user = get_object_or_404(CustomUser, id=user_id)
            # Check if user has provider profile or skill swap listing
            if hasattr(user, 'provider_profile'):
                return user.provider_profile
            return user
        return None
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['provider'] = self.get_provider()
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        provider = self.get_provider()
        context['provider'] = provider
        
        # Check provider preferences
        if provider and hasattr(provider, 'provider_profile'):
            profile = provider.provider_profile
            context['accepts_paid'] = profile.accepts_paid_jobs
            context['accepts_credits'] = profile.accepts_credit_jobs
            context['accepts_barter'] = profile.accepts_barter
        elif isinstance(provider, type(self.request.user)):
            # User-based provider (for skill swaps)
            context['accepts_paid'] = False
            context['accepts_credits'] = hasattr(provider, 'skill_swap_listing') and provider.skill_swap_listing.is_active
            context['accepts_barter'] = hasattr(provider, 'skill_swap_listing') and provider.skill_swap_listing.is_active
        
        return context
    
    def form_valid(self, form):
        form.instance.requester = self.request.user
        provider = self.get_provider()
        
        if isinstance(provider, ServiceProvider):
            # Provider profile
            if provider.user:
                form.instance.provider = provider.user
        elif provider:
            # User (for skill swaps)
            form.instance.provider = provider
        
        # Handle credit escrow for credit-based jobs
        if form.instance.payment_type == 'credit' and form.instance.credits_requested:
            # Check balance
            balance = CreditTransactionService.get_available_balance(self.request.user)
            if balance < form.instance.credits_requested:
                form.add_error(
                    'credits_requested',
                    f'Insufficient credits. Available: {balance}, Required: {form.instance.credits_requested}'
                )
                return self.form_invalid(form)
            
            # Create escrow hold
            form.instance.credits_in_escrow = form.instance.credits_requested
        
        messages.success(self.request, 'Job request created! The provider will be notified.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('providers:unified_job_detail', kwargs={'pk': self.object.pk})


class UnifiedJobDetailView(LoginRequiredMixin, DetailView):
    """View details of a unified job."""
    
    model = UnifiedJob
    template_name = 'providers/jobs/unified_job_detail.html'
    context_object_name = 'job'
    
    def get_queryset(self):
        """User can only view jobs they're involved in."""
        return UnifiedJob.objects.filter(
            Q(requester=self.request.user) | Q(provider=self.request.user)
        ).select_related('requester', 'provider').prefetch_related('proposals', 'messages')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job = self.object
        
        # Determine user role
        context['is_requester'] = job.requester == self.request.user
        context['is_provider'] = job.provider == self.request.user if job.provider else False
        
        # Get proposals
        context['proposals'] = job.proposals.all().order_by('-created_at')
        context['current_proposal'] = job.get_current_proposal()
        
        # Get messages
        context['messages'] = job.messages.all().order_by('created_at')
        
        # Forms
        if context['is_provider'] and job.status == 'pending':
            context['proposal_form'] = JobProposalForm(job=job, proposed_by=self.request.user)
        context['message_form'] = JobMessageForm()
        
        # Check if can confirm completion
        context['can_confirm'] = (
            job.status == 'completed' and
            not (job.requester_confirmed and job.provider_confirmed)
        )
        
        return context


class UnifiedJobListView(LoginRequiredMixin, ListView):
    """Dashboard showing all jobs (paid/credit/barter) in one place."""
    
    model = UnifiedJob
    template_name = 'providers/jobs/unified_job_dashboard.html'
    context_object_name = 'jobs'
    paginate_by = 20
    
    def get_queryset(self):
        """Get user's jobs (as requester or provider)."""
        queryset = UnifiedJob.objects.filter(
            Q(requester=self.request.user) | Q(provider=self.request.user)
        ).select_related('requester', 'provider')
        
        # Filter by status
        status_filter = self.request.GET.get('status', 'all')
        if status_filter != 'all':
            queryset = queryset.filter(status=status_filter)
        
        # Filter by payment type
        type_filter = self.request.GET.get('type', 'all')
        if type_filter != 'all':
            queryset = queryset.filter(payment_type=type_filter)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Statistics
        all_jobs = UnifiedJob.objects.filter(
            Q(requester=user) | Q(provider=user)
        )
        
        context['stats'] = {
            'total': all_jobs.count(),
            'pending': all_jobs.filter(status='pending').count(),
            'in_progress': all_jobs.filter(status='in_progress').count(),
            'completed': all_jobs.filter(status='completed').count(),
            'paid': all_jobs.filter(payment_type='paid').count(),
            'credit': all_jobs.filter(payment_type='credit').count(),
            'barter': all_jobs.filter(payment_type='barter').count(),
        }
        
        return context


@login_required
@require_POST
def submit_job_proposal(request, job_id):
    """Submit a proposal or counter-offer for a job."""
    job = get_object_or_404(
        UnifiedJob.objects.filter(
            Q(requester=request.user) | Q(provider=request.user)
        ),
        pk=job_id
    )
    
    # Only provider can submit proposals
    if job.provider != request.user:
        messages.error(request, 'Only the provider can submit proposals.')
        return redirect('providers:unified_job_detail', pk=job.pk)
    
    form = JobProposalForm(request.POST, job=job, proposed_by=request.user)
    
    if form.is_valid():
        proposal = form.save(commit=False)
        proposal.job = job
        proposal.proposed_by = request.user
        
        # Determine proposal type
        if job.proposals.exists():
            proposal.proposal_type = 'counter'
        else:
            proposal.proposal_type = 'initial'
        
        proposal.save()
        
        # Update job status
        job.status = 'proposed'
        job.save()
        
        # Create notification message
        JobMessage.objects.create(
            job=job,
            sender=request.user,
            recipient=job.requester,
            message=f"New proposal submitted: {proposal.message[:100]}",
            related_proposal=proposal
        )
        
        messages.success(request, 'Proposal submitted successfully!')
    else:
        messages.error(request, 'Please correct the errors below.')
    
    return redirect('providers:unified_job_detail', pk=job.pk)


@login_required
@require_POST
def respond_to_proposal(request, proposal_id, action):
    """Respond to a proposal (accept/decline)."""
    proposal = get_object_or_404(
        JobProposal.objects.filter(
            Q(job__requester=request.user) | Q(job__provider=request.user)
        ),
        pk=proposal_id
    )
    
    job = proposal.job
    
    # Only requester can respond to proposals
    if job.requester != request.user:
        messages.error(request, 'Only the requester can respond to proposals.')
        return redirect('providers:unified_job_detail', pk=job.pk)
    
    if action == 'accept':
        proposal.status = 'accepted'
        proposal.responded_at = timezone.now()
        proposal.save()
        
        # Update job with accepted terms
        job.status = 'accepted'
        job.accepted_at = timezone.now()
        job.provider = proposal.proposed_by
        
        if job.payment_type == 'paid':
            job.agreed_amount = proposal.proposed_amount
        elif job.payment_type == 'credit':
            job.credits_agreed = proposal.proposed_credits
            job.credits_in_escrow = proposal.proposed_credits
        elif job.payment_type == 'barter':
            job.barter_offer = proposal.proposed_barter_offer
            job.barter_request = proposal.proposed_barter_request
        
        job.save()
        
        # Create escrow for credit jobs
        if job.payment_type == 'credit' and job.credits_agreed:
            # Create skill swap job for credit processing
            swap_job = SkillSwapJob.objects.create(
                requester=job.requester,
                provider=job.provider,
                title=job.title,
                description=job.description,
                hours_required=job.credits_agreed or job.credits_requested,
                status='accepted',
                credits_in_escrow=job.credits_agreed or job.credits_requested,
            )
            job.related_skill_swap_job = swap_job
            job.status = 'in_progress'
            job.started_at = timezone.now()
            job.save()
            
            # Create escrow hold
            success, error, escrow = CreditTransactionService.create_escrow_hold(swap_job)
            if not success:
                messages.warning(request, f'Escrow creation warning: {error}')
        
        messages.success(request, 'Proposal accepted! Job is now active.')
    
    elif action == 'decline':
        proposal.status = 'declined'
        proposal.responded_at = timezone.now()
        proposal.save()
        messages.info(request, 'Proposal declined.')
    
    return redirect('providers:unified_job_detail', pk=job.pk)


@login_required
@require_POST
def send_job_message(request, job_id):
    """Send a message in the job thread."""
    job = get_object_or_404(
        UnifiedJob.objects.filter(
            Q(requester=request.user) | Q(provider=request.user)
        ),
        pk=job_id
    )
    
    form = JobMessageForm(request.POST)
    
    if form.is_valid():
        message = form.save(commit=False)
        message.job = job
        message.sender = request.user
        message.recipient = job.provider if job.requester == request.user else job.requester
        message.save()
        
        messages.success(request, 'Message sent!')
    else:
        messages.error(request, 'Please enter a message.')
    
    return redirect('providers:unified_job_detail', pk=job.pk)


@login_required
@require_POST
def confirm_job_completion(request, job_id):
    """Confirm job completion to release payment/credits."""
    job = get_object_or_404(
        UnifiedJob.objects.filter(
            Q(requester=request.user) | Q(provider=request.user)
        ),
        pk=job_id
    )
    
    if request.user == job.requester:
        job.requester_confirmed = True
    elif request.user == job.provider:
        job.provider_confirmed = True
    
    # If both confirmed, process payment/credits
    if job.requester_confirmed and job.provider_confirmed:
        job.status = 'completed'
        job.completed_at = timezone.now()
        
        # Process payment based on type
        if job.payment_type == 'paid':
            # TODO: Integrate with payment processing
            job.payment_processed = True
            job.payment_processed_at = timezone.now()
            messages.success(request, 'Job completed! Payment will be processed.')
        
        elif job.payment_type == 'credit':
            # Release escrow and transfer credits
            if job.related_skill_swap_job:
                # Update swap job status
                swap_job = job.related_skill_swap_job
                swap_job.status = 'completed'
                swap_job.requester_confirmed = job.requester_confirmed
                swap_job.provider_confirmed = job.provider_confirmed
                swap_job.save()
                
                success, error = CreditTransactionService.release_escrow(swap_job)
                if success:
                    messages.success(request, 'Job completed! Credits have been transferred.')
                else:
                    messages.error(request, f'Error releasing credits: {error}')
        
        elif job.payment_type == 'barter':
            messages.success(request, 'Barter exchange completed!')
    
    else:
        messages.info(request, 'Completion confirmed. Waiting for other party to confirm.')
    
    job.save()
    return redirect('providers:unified_job_detail', pk=job.pk)
