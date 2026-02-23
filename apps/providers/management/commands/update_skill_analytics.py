"""
Management command to update skill supply and demand analytics.
Run daily via cron or scheduled task.
"""

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone
from collections import defaultdict

from apps.accounts.modes_models import Skill
from apps.accounts.models import CustomUser
from apps.providers.analytics_service import SkillAnalyticsService


class Command(BaseCommand):
    help = 'Update skill supply and demand analytics for all active skills and geographic areas'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days-back',
            type=int,
            default=30,
            help='Number of days to look back for analytics (default: 30)',
        )
        parser.add_argument(
            '--city',
            type=str,
            help='Update analytics for specific city only',
        )
        parser.add_argument(
            '--state',
            type=str,
            help='Update analytics for specific state only',
        )
        parser.add_argument(
            '--skill',
            type=str,
            help='Update analytics for specific skill slug only',
        )
        parser.add_argument(
            '--radius',
            type=int,
            default=25,
            help='Radius in miles for geographic area (default: 25)',
        )
    
    def handle(self, *args, **options):
        days_back = options['days_back']
        city_filter = options.get('city')
        state_filter = options.get('state')
        skill_filter = options.get('skill')
        radius = options['radius']
        
        self.stdout.write(f'Starting skill analytics update (days_back={days_back}, radius={radius}mi)...')
        
        # Get skills to process
        skills = Skill.objects.filter(is_active=True)
        if skill_filter:
            skills = skills.filter(slug=skill_filter)
        
        skill_count = skills.count()
        self.stdout.write(f'Processing {skill_count} skills...')
        
        # Get unique geographic areas from users and providers
        locations = self._get_locations(city_filter, state_filter)
        location_count = len(locations)
        self.stdout.write(f'Processing {location_count} geographic areas...')
        
        total_updates = 0
        errors = 0
        
        for skill in skills:
            for city, state, zip_code in locations:
                try:
                    SkillAnalyticsService.update_skill_analytics(
                        skill=skill,
                        city=city,
                        state=state,
                        zip_code=zip_code,
                        radius_miles=radius,
                        days_back=days_back
                    )
                    total_updates += 1
                    
                    if total_updates % 10 == 0:
                        self.stdout.write(f'  Updated {total_updates} records...')
                
                except Exception as e:
                    errors += 1
                    self.stdout.write(
                        self.style.ERROR(f'Error updating {skill.name} in {city}, {state}: {str(e)}')
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted! Updated {total_updates} records with {errors} errors.'
            )
        )
    
    def _get_locations(self, city_filter=None, state_filter=None):
        """Get unique locations from users and providers."""
        locations = set()
        
        # Get locations from users
        users = CustomUser.objects.exclude(
            Q(city__isnull=True) | Q(city='') |
            Q(state__isnull=True) | Q(state='')
        )
        
        if city_filter:
            users = users.filter(city__iexact=city_filter)
        if state_filter:
            users = users.filter(state__iexact=state_filter)
        
        for user in users.values('city', 'state', 'zip_code').distinct():
            locations.add((
                user['city'],
                user['state'],
                user.get('zip_code') or ''
            ))
        
        # Get locations from providers
        from apps.providers.models import ServiceProvider
        providers = ServiceProvider.objects.filter(
            is_active=True
        ).exclude(
            Q(city__isnull=True) | Q(city='') |
            Q(state__isnull=True) | Q(state='')
        )
        
        if city_filter:
            providers = providers.filter(city__iexact=city_filter)
        if state_filter:
            providers = providers.filter(state__iexact=state_filter)
        
        for provider in providers.values('city', 'state', 'zip_code').distinct():
            locations.add((
                provider['city'],
                provider['state'],
                provider.get('zip_code') or ''
            ))
        
        return list(locations)
