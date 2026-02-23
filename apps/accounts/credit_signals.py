"""
Signals for automatic credit management.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .modes_models import SkillSwapListing, SkillSwapJob
from .credit_service import CreditTransactionService


@receiver(post_save, sender=SkillSwapListing)
def award_welcome_bonus(sender, instance, created, **kwargs):
    """Award 5 bonus credits to new users when they create a skill swap listing."""
    if created:
        # Award welcome bonus
        CreditTransactionService.award_bonus_credits(
            user=instance.user,
            credits=5,
            description="Welcome bonus - Start swapping skills!"
        )


@receiver(post_save, sender=SkillSwapJob)
def handle_job_status_change(sender, instance, created, **kwargs):
    """Handle automatic credit transfers based on job status changes."""
    if created:
        # New job posted - create escrow hold
        if instance.status == 'posted':
            success, error, escrow_credit = CreditTransactionService.create_escrow_hold(instance)
            if not success:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to create escrow for job {instance.id}: {error}")
    else:
        # Job status changed - check if completion was just confirmed
        if instance.status == 'completed':
            # Check if both parties confirmed
            if instance.requester_confirmed and instance.provider_confirmed:
                # Release escrow and transfer credits
                success, error = CreditTransactionService.release_escrow(instance)
                if not success:
                    # Log error but don't raise exception
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Failed to release escrow for job {instance.id}: {error}")
        
        elif instance.status == 'cancelled':
            # Refund escrow only if credits are still in escrow
            if instance.credits_in_escrow > 0:
                success, error = CreditTransactionService.refund_escrow(
                    instance,
                    reason="Job cancelled by user"
                )
                if not success:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Failed to refund escrow for job {instance.id}: {error}")
