"""
Service for calculating skill supply and demand analytics.
"""

from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from collections import defaultdict

from .skill_analytics import SkillDemand, SkillSupply, SkillMarketOpportunity
from .models import ServiceProvider
from .unified_jobs import UnifiedJob
from apps.accounts.modes_models import SkillSwapListing, FreelanceListing, Skill


class SkillAnalyticsService:
    """Service for calculating and updating skill analytics."""
    
    @staticmethod
    def calculate_demand_score(skill, city, state, zip_code=None, radius_miles=25, days_back=30):
        """
        Calculate demand score for a skill in a geographic area.
        
        Args:
            skill: Skill instance
            city: City name
            state: State name
            zip_code: Optional ZIP code
            radius_miles: Radius in miles (default 25)
            days_back: Number of days to look back (default 30)
        
        Returns:
            dict with demand metrics
        """
        period_end = timezone.now()
        period_start = period_end - timedelta(days=days_back)
        
        # Initialize counters
        job_requests_count = 0
        skill_swap_wants_count = 0
        
        # Count from unified job requests
        # Look for jobs mentioning this skill or in related categories
        job_requests = UnifiedJob.objects.filter(
            created_at__gte=period_start,
            created_at__lte=period_end,
            service_city__iexact=city,
            service_state__iexact=state,
        )
        
        if zip_code:
            job_requests = job_requests.filter(service_zip__startswith=zip_code[:5])
        
        # Check if skill name appears in job descriptions or titles
        skill_name_lower = skill.name.lower()
        for job in job_requests:
            if (skill_name_lower in job.title.lower() or 
                skill_name_lower in job.description.lower()):
                job_requests_count += 1
        
        # Count from skill swap listings (skills_wanted)
        skill_swap_wants = SkillSwapListing.objects.filter(
            is_active=True,
            skills_wanted=skill
        ).filter(
            Q(user__city__iexact=city) | Q(user__state__iexact=state)
        )
        
        if zip_code:
            skill_swap_wants = skill_swap_wants.filter(
                Q(user__zip_code__startswith=zip_code[:5])
            )
        
        skill_swap_wants_count = skill_swap_wants.count()
        
        # Calculate demand score
        # Weight: job requests = 2 points, skill swap wants = 1 point
        total_demand_signals = job_requests_count + skill_swap_wants_count
        demand_score = (job_requests_count * 2) + skill_swap_wants_count
        
        return {
            'demand_score': Decimal(str(demand_score)),
            'job_requests_count': job_requests_count,
            'skill_swap_wants_count': skill_swap_wants_count,
            'total_demand_signals': total_demand_signals,
            'period_start': period_start,
            'period_end': period_end,
        }
    
    @staticmethod
    def calculate_supply_score(skill, city, state, zip_code=None, radius_miles=25, days_back=30):
        """
        Calculate supply score for a skill in a geographic area.
        
        Args:
            skill: Skill instance
            city: City name
            state: State name
            zip_code: Optional ZIP code
            radius_miles: Radius in miles (default 25)
            days_back: Number of days to look back (default 30)
        
        Returns:
            dict with supply metrics
        """
        period_end = timezone.now()
        period_start = period_end - timedelta(days=days_back)
        
        # Count from service providers
        # Check if skill appears in provider skills or description
        providers = ServiceProvider.objects.filter(
            is_active=True,
            city__iexact=city,
            state__iexact=state,
        )
        
        if zip_code:
            providers = providers.filter(zip_code__startswith=zip_code[:5])
        
        skill_name_lower = skill.name.lower()
        provider_count = 0
        for provider in providers:
            if (skill_name_lower in provider.skills.lower() or
                skill_name_lower in provider.description.lower()):
                provider_count += 1
        
        # Count from skill swap listings (skills_offered)
        skill_swap_offers = SkillSwapListing.objects.filter(
            is_active=True,
            skills_offered=skill
        ).filter(
            Q(user__city__iexact=city) | Q(user__state__iexact=state)
        )
        
        if zip_code:
            skill_swap_offers = skill_swap_offers.filter(
                Q(user__zip_code__startswith=zip_code[:5])
            )
        
        skill_swap_offers_count = skill_swap_offers.count()
        
        # Count from freelance listings
        freelance_listings = FreelanceListing.objects.filter(
            is_active=True,
            skills=skill
        ).filter(
            Q(user__city__iexact=city) | Q(user__state__iexact=state)
        )
        
        if zip_code:
            freelance_listings = freelance_listings.filter(
                Q(user__zip_code__startswith=zip_code[:5])
            )
        
        freelance_listings_count = freelance_listings.count()
        
        # Calculate supply score
        # Weight: providers = 3 points, skill swap offers = 1 point, freelance = 2 points
        total_supply_signals = provider_count + skill_swap_offers_count + freelance_listings_count
        supply_score = (provider_count * 3) + skill_swap_offers_count + (freelance_listings_count * 2)
        
        return {
            'supply_score': Decimal(str(supply_score)),
            'provider_count': provider_count,
            'skill_swap_offers_count': skill_swap_offers_count,
            'freelance_listings_count': freelance_listings_count,
            'total_supply_signals': total_supply_signals,
            'period_start': period_start,
            'period_end': period_end,
        }
    
    @staticmethod
    def update_skill_analytics(skill, city, state, zip_code=None, radius_miles=25, days_back=30):
        """
        Update analytics for a specific skill in a geographic area.
        
        Returns:
            tuple: (demand_record, supply_record, opportunity_record)
        """
        # Calculate demand
        demand_data = SkillAnalyticsService.calculate_demand_score(
            skill, city, state, zip_code, radius_miles, days_back
        )
        
        # Get previous period for trend calculation
        previous_demand = SkillDemand.objects.filter(
            skill=skill,
            city=city,
            state=state,
            zip_code=zip_code or '',
        ).order_by('-calculated_at').first()
        
        demand_change_percent = None
        if previous_demand and previous_demand.demand_score > 0:
            change = demand_data['demand_score'] - previous_demand.demand_score
            demand_change_percent = (change / previous_demand.demand_score) * 100
        
        # Create or update demand record
        demand_record, _ = SkillDemand.objects.update_or_create(
            skill=skill,
            city=city,
            state=state,
            zip_code=zip_code or '',
            period_start=demand_data['period_start'],
            period_end=demand_data['period_end'],
            defaults={
                'radius_miles': radius_miles,
                'demand_score': demand_data['demand_score'],
                'job_requests_count': demand_data['job_requests_count'],
                'skill_swap_wants_count': demand_data['skill_swap_wants_count'],
                'total_demand_signals': demand_data['total_demand_signals'],
                'previous_demand_score': previous_demand.demand_score if previous_demand else None,
                'demand_change_percent': demand_change_percent,
            }
        )
        
        # Calculate supply
        supply_data = SkillAnalyticsService.calculate_supply_score(
            skill, city, state, zip_code, radius_miles, days_back
        )
        
        # Get previous period for trend calculation
        previous_supply = SkillSupply.objects.filter(
            skill=skill,
            city=city,
            state=state,
            zip_code=zip_code or '',
        ).order_by('-calculated_at').first()
        
        supply_change_percent = None
        if previous_supply and previous_supply.supply_score > 0:
            change = supply_data['supply_score'] - previous_supply.supply_score
            supply_change_percent = (change / previous_supply.supply_score) * 100
        
        # Create or update supply record
        supply_record, _ = SkillSupply.objects.update_or_create(
            skill=skill,
            city=city,
            state=state,
            zip_code=zip_code or '',
            period_start=supply_data['period_start'],
            period_end=supply_data['period_end'],
            defaults={
                'radius_miles': radius_miles,
                'supply_score': supply_data['supply_score'],
                'provider_count': supply_data['provider_count'],
                'skill_swap_offers_count': supply_data['skill_swap_offers_count'],
                'freelance_listings_count': supply_data['freelance_listings_count'],
                'total_supply_signals': supply_data['total_supply_signals'],
                'previous_supply_score': previous_supply.supply_score if previous_supply else None,
                'supply_change_percent': supply_change_percent,
            }
        )
        
        # Calculate opportunity score
        # High opportunity = high demand, low supply
        opportunity_score = Decimal('0')
        if supply_record.supply_score > 0:
            opportunity_score = demand_record.demand_score / supply_record.supply_score
        elif demand_record.demand_score > 0:
            opportunity_score = demand_record.demand_score * 10  # High opportunity if no supply
        
        # Determine market status
        if demand_record.demand_score > supply_record.supply_score * 1.5:
            market_status = 'high_opportunity'
        elif supply_record.supply_score > demand_record.demand_score * 1.5:
            market_status = 'oversupplied'
        elif demand_record.demand_score == 0 and supply_record.supply_score == 0:
            market_status = 'emerging'
        else:
            market_status = 'balanced'
        
        # Create or update opportunity record
        opportunity_record, _ = SkillMarketOpportunity.objects.update_or_create(
            skill=skill,
            city=city,
            state=state,
            zip_code=zip_code or '',
            period_start=demand_data['period_start'],
            period_end=demand_data['period_end'],
            defaults={
                'demand_score': demand_record.demand_score,
                'supply_score': supply_record.supply_score,
                'opportunity_score': opportunity_score,
                'market_status': market_status,
            }
        )
        
        return demand_record, supply_record, opportunity_record
    
    @staticmethod
    def get_top_opportunities(city, state, zip_code=None, limit=10):
        """Get top skill opportunities in an area."""
        opportunities = SkillMarketOpportunity.objects.filter(
            city__iexact=city,
            state__iexact=state,
        )
        
        if zip_code:
            opportunities = opportunities.filter(zip_code__startswith=zip_code[:5])
        
        return opportunities.filter(
            market_status='high_opportunity'
        ).order_by('-opportunity_score')[:limit]
    
    @staticmethod
    def get_trending_skills(city, state, zip_code=None, limit=10):
        """Get trending skills (demand increasing)."""
        demands = SkillDemand.objects.filter(
            city__iexact=city,
            state__iexact=state,
            demand_change_percent__gt=10,  # >10% increase
        )
        
        if zip_code:
            demands = demands.filter(zip_code__startswith=zip_code[:5])
        
        return demands.order_by('-demand_change_percent')[:limit]
    
    @staticmethod
    def get_user_skill_opportunities(user, limit=10):
        """Get opportunities for skills the user offers."""
        if not hasattr(user, 'skill_swap_listing') or not user.skill_swap_listing.is_active:
            return []
        
        user_skills = user.skill_swap_listing.skills_offered.all()
        city = user.city or ''
        state = user.state or ''
        zip_code = user.zip_code or ''
        
        opportunities = []
        for skill in user_skills:
            opp = SkillMarketOpportunity.objects.filter(
                skill=skill,
                city__iexact=city,
                state__iexact=state,
            ).order_by('-calculated_at').first()
            
            if opp:
                opportunities.append(opp)
        
        # Sort by opportunity score
        opportunities.sort(key=lambda x: x.opportunity_score, reverse=True)
        return opportunities[:limit]
