"""
Management command to send weekly match notification emails.
"""

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from apps.accounts.models import CustomUser
from apps.accounts.matching_service import MatchingService


class Command(BaseCommand):
    help = 'Send weekly match notification emails to users with new matches'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending emails',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days to look back for new matches (default: 7)',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        days = options['days']
        
        self.stdout.write(f'Finding users with new matches in the last {days} days...')
        
        # Get all active users
        users = CustomUser.objects.filter(is_active=True)
        
        emails_sent = 0
        total_matches = 0
        
        for user in users:
            matching_service = MatchingService(user)
            new_matches_count = matching_service.get_new_matches_count(days=days)
            
            if new_matches_count > 0:
                total_matches += new_matches_count
                
                # Build email content
                # Use request.build_absolute_uri if available, otherwise construct URL
                try:
                    from django.contrib.sites.models import Site
                    current_site = Site.objects.get_current()
                    site_url = f"http://{current_site.domain}"
                except:
                    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
                
                matches_url = site_url + reverse('accounts:match_suggestions')
                
                subject = f'You have {new_matches_count} new potential match{"es" if new_matches_count > 1 else ""} on FindAPro!'
                
                message = f'''
Hello {user.full_name},

Great news! We found {new_matches_count} new potential match{"es" if new_matches_count > 1 else ""} for you based on your skills and preferences.

View your matches: {matches_url}

These matches are based on:
- Skill compatibility
- Geographic proximity
- Reputation and ratings
- Availability alignment

Don't miss out on great collaboration opportunities!

Best regards,
FindAPro Team
                '''.strip()
                
                if dry_run:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'[DRY RUN] Would send to {user.email}: {new_matches_count} matches'
                        )
                    )
                else:
                    try:
                        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@findapro.com')
                        send_mail(
                            subject=subject,
                            message=message,
                            from_email=from_email,
                            recipient_list=[user.email],
                            fail_silently=False,
                        )
                        emails_sent += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Sent to {user.email}: {new_matches_count} matches'
                            )
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f'✗ Failed to send to {user.email}: {str(e)}'
                            )
                        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'\n[DRY RUN] Would send {emails_sent} emails about {total_matches} total matches'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Sent {emails_sent} emails about {total_matches} total matches'
                )
            )
