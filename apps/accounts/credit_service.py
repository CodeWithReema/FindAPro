"""
Credit transaction service for time-banking system.
"""

from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import CustomUser
from .modes_models import SkillSwapListing, SkillCredit, SkillSwapJob


class CreditTransactionService:
    """Service for processing credit transactions with balance validation."""
    
    @staticmethod
    @transaction.atomic
    def process_transaction(
        credit_transaction,
        check_balance=True,
        auto_approve=False
    ):
        """
        Process a credit transaction.
        
        Args:
            credit_transaction: SkillCredit instance
            check_balance: Whether to check if user has sufficient balance
            auto_approve: Whether to auto-approve the transaction
        
        Returns:
            tuple: (success: bool, error_message: str)
        """
        if credit_transaction.status == 'approved':
            return True, None
        
        # Check balance for spent transactions
        if check_balance and credit_transaction.transaction_type == 'spent':
            balance = CreditTransactionService.get_user_balance(credit_transaction.to_user)
            if balance < credit_transaction.credits:
                return False, f"Insufficient balance. Available: {balance}, Required: {credit_transaction.credits}"
        
        # Check balance for escrow holds
        if check_balance and credit_transaction.transaction_type == 'escrow_hold':
            balance = CreditTransactionService.get_user_balance(credit_transaction.to_user)
            if balance < credit_transaction.credits:
                return False, f"Insufficient balance for escrow. Available: {balance}, Required: {credit_transaction.credits}"
        
        # Auto-approve if requested
        if auto_approve:
            credit_transaction.status = 'approved'
            credit_transaction.verified_at = timezone.now()
        
        credit_transaction.save()
        return True, None
    
    @staticmethod
    def get_user_balance(user):
        """
        Calculate user's current credit balance.
        
        Returns:
            Decimal: Current balance (earned - spent)
        """
        if not hasattr(user, 'skill_swap_listing'):
            return Decimal('0')
        
        listing = user.skill_swap_listing
        return listing.credits_earned - listing.credits_spent
    
    @staticmethod
    def get_pending_credits(user):
        """
        Get credits held in escrow (pending jobs).
        
        Returns:
            Decimal: Total credits in escrow
        """
        pending_jobs = SkillSwapJob.objects.filter(
            requester=user,
            status__in=['accepted', 'in_progress'],
            credits_in_escrow__gt=0
        )
        return sum(job.credits_in_escrow for job in pending_jobs)
    
    @staticmethod
    def get_available_balance(user):
        """
        Get available balance (total balance minus escrow).
        
        Returns:
            Decimal: Available credits
        """
        balance = CreditTransactionService.get_user_balance(user)
        escrow = CreditTransactionService.get_pending_credits(user)
        return max(Decimal('0'), balance - escrow)
    
    @staticmethod
    @transaction.atomic
    def award_bonus_credits(user, credits, description="Welcome bonus"):
        """
        Award bonus credits to a new user.
        
        Args:
            user: CustomUser instance
            credits: Number of credits to award
            description: Description of the bonus
        
        Returns:
            SkillCredit: Created credit transaction
        """
        credit = SkillCredit.objects.create(
            from_user=None,  # System transaction
            to_user=user,
            transaction_type='bonus',
            credits=credits,
            description=description,
            status='approved',
            verified_at=timezone.now(),
            verified_by=None,  # System
        )
        return credit
    
    @staticmethod
    @transaction.atomic
    def create_escrow_hold(job):
        """
        Create escrow hold for a job.
        
        Args:
            job: SkillSwapJob instance
        
        Returns:
            tuple: (success: bool, error_message: str, credit_transaction: SkillCredit)
        """
        credits = job.credits_required
        
        # Check balance
        balance = CreditTransactionService.get_available_balance(job.requester)
        if balance < credits:
            return False, f"Insufficient balance. Available: {balance}, Required: {credits}", None
        
        # Create escrow hold transaction
        escrow_credit = SkillCredit.objects.create(
            from_user=job.requester,
            to_user=job.requester,  # Hold credits for requester
            job=job,
            transaction_type='escrow_hold',
            credits=credits,
            description=f"Escrow hold for job: {job.title}",
            status='approved',
            verified_at=timezone.now(),
        )
        
        # Update job escrow amount
        job.credits_in_escrow = credits
        job.save()
        
        return True, None, escrow_credit
    
    @staticmethod
    @transaction.atomic
    def release_escrow(job, confirm_by_requester=True):
        """
        Release escrow and transfer credits to provider.
        
        Args:
            job: SkillSwapJob instance
            confirm_by_requester: Whether requester confirmed completion
        
        Returns:
            tuple: (success: bool, error_message: str)
        """
        if job.status != 'completed':
            return False, "Job must be completed before releasing escrow"
        
        if not (job.requester_confirmed and job.provider_confirmed):
            return False, "Both parties must confirm completion"
        
        credits = job.credits_in_escrow
        if credits <= 0:
            return False, "No credits in escrow"
        
        # Create escrow release transaction (deduct from requester)
        release_credit = SkillCredit.objects.create(
            from_user=job.requester,
            to_user=job.requester,
            job=job,
            transaction_type='escrow_release',
            credits=credits,
            description=f"Escrow release for job: {job.title}",
            status='approved',
            verified_at=timezone.now(),
        )
        
        # Create earned credit for provider
        earned_credit = SkillCredit.objects.create(
            from_user=job.requester,
            to_user=job.provider,
            job=job,
            transaction_type='earned',
            credits=credits,
            skill_swapped=job.skill_needed,
            description=f"Earned credits for completing: {job.title}",
            swap_date=timezone.now().date(),
            status='approved',
            verified_at=timezone.now(),
        )
        
        # Create spent credit for requester
        spent_credit = SkillCredit.objects.create(
            from_user=job.provider,
            to_user=job.requester,
            job=job,
            transaction_type='spent',
            credits=credits,
            skill_swapped=job.skill_needed,
            description=f"Spent credits for: {job.title}",
            swap_date=timezone.now().date(),
            status='approved',
            verified_at=timezone.now(),
        )
        
        # Clear escrow
        job.credits_in_escrow = Decimal('0')
        job.save()
        
        return True, None
    
    @staticmethod
    @transaction.atomic
    def refund_escrow(job, reason="Job cancelled"):
        """
        Refund escrow credits back to requester.
        
        Args:
            job: SkillSwapJob instance
            reason: Reason for refund
        
        Returns:
            tuple: (success: bool, error_message: str)
        """
        credits = job.credits_in_escrow
        if credits <= 0:
            return False, "No credits in escrow to refund"
        
        # Create refund transaction
        refund_credit = SkillCredit.objects.create(
            from_user=None,  # System
            to_user=job.requester,
            job=job,
            transaction_type='refund',
            credits=credits,
            description=f"Refund for cancelled job: {job.title}. Reason: {reason}",
            status='approved',
            verified_at=timezone.now(),
        )
        
        # Clear escrow
        job.credits_in_escrow = Decimal('0')
        job.status = 'cancelled'
        job.cancelled_at = timezone.now()
        job.save()
        
        return True, None
    
    @staticmethod
    @transaction.atomic
    def admin_adjustment(user, credits, description, admin_user, notes=""):
        """
        Admin manual credit adjustment.
        
        Args:
            user: CustomUser to adjust
            credits: Amount (positive or negative)
            description: Description of adjustment
            admin_user: Admin making the adjustment
            notes: Additional notes
        
        Returns:
            SkillCredit: Created credit transaction
        """
        credit = SkillCredit.objects.create(
            from_user=None,  # System/admin
            to_user=user,
            transaction_type='adjustment',
            credits=abs(credits),
            description=description,
            admin_notes=notes,
            status='approved',
            verified_by=admin_user,
            verified_at=timezone.now(),
        )
        return credit
    
    @staticmethod
    def get_transaction_history(user, transaction_type=None, limit=50):
        """
        Get user's transaction history.
        
        Args:
            user: CustomUser instance
            transaction_type: Optional filter by type
            limit: Maximum number of transactions
        
        Returns:
            QuerySet: SkillCredit queryset
        """
        queryset = SkillCredit.objects.filter(
            to_user=user
        ).select_related('from_user', 'job', 'skill_swapped')
        
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        return queryset.order_by('-created_at')[:limit]
    
    @staticmethod
    def get_credits_summary(user, days=30):
        """
        Get credits summary for dashboard.
        
        Args:
            user: CustomUser instance
            days: Number of days to look back
        
        Returns:
            dict: Summary statistics
        """
        from django.db.models import Sum, Q
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        transactions = SkillCredit.objects.filter(
            to_user=user,
            status='approved',
            created_at__gte=cutoff_date
        )
        
        earned = transactions.filter(
            transaction_type__in=['earned', 'bonus', 'refund']
        ).aggregate(total=Sum('credits'))['total'] or Decimal('0')
        
        spent = transactions.filter(
            transaction_type__in=['spent', 'escrow_hold']
        ).aggregate(total=Sum('credits'))['total'] or Decimal('0')
        
        return {
            'balance': CreditTransactionService.get_user_balance(user),
            'available_balance': CreditTransactionService.get_available_balance(user),
            'pending_credits': CreditTransactionService.get_pending_credits(user),
            'earned_last_30_days': earned,
            'spent_last_30_days': spent,
            'net_change': earned - spent,
        }
