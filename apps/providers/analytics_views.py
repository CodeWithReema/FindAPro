"""
Views for skill analytics dashboard.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from .analytics_service import SkillAnalyticsService
from .skill_analytics import SkillDemand, SkillSupply, SkillMarketOpportunity
from apps.accounts.modes_models import Skill


class SkillAnalyticsDashboardView(LoginRequiredMixin, TemplateView):
    """Main analytics dashboard showing skill supply and demand."""
    
    template_name = 'providers/analytics/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user location
        city = self.request.GET.get('city', user.city or '')
        state = self.request.GET.get('state', user.state or '')
        zip_code = self.request.GET.get('zip_code', user.zip_code or '')
        radius = int(self.request.GET.get('radius', 25))
        days_back = int(self.request.GET.get('days_back', 30))
        
        if not city or not state:
            # Default to a common location if user hasn't set one
            city = 'San Francisco'
            state = 'CA'
        
        context['city'] = city
        context['state'] = state
        context['zip_code'] = zip_code
        context['radius'] = radius
        context['days_back'] = days_back
        
        # Get top opportunities (high demand, low supply)
        top_opportunities = SkillAnalyticsService.get_top_opportunities(
            city, state, zip_code, limit=10
        )
        context['top_opportunities'] = top_opportunities
        
        # Get trending skills (demand increasing)
        trending_skills = SkillAnalyticsService.get_trending_skills(
            city, state, zip_code, limit=10
        )
        context['trending_skills'] = trending_skills
        
        # Get oversupplied skills
        oversupplied = SkillMarketOpportunity.objects.filter(
            city__iexact=city,
            state__iexact=state,
            market_status='oversupplied',
        )
        if zip_code:
            oversupplied = oversupplied.filter(zip_code__startswith=zip_code[:5])
        context['oversupplied_skills'] = oversupplied.order_by('-supply_score')[:10]
        
        # Get user's skill opportunities
        user_opportunities = SkillAnalyticsService.get_user_skill_opportunities(user, limit=10)
        context['user_opportunities'] = user_opportunities
        
        # Get user's skills
        user_skills = []
        if hasattr(user, 'skill_swap_listing') and user.skill_swap_listing.is_active:
            user_skills = list(user.skill_swap_listing.skills_offered.all())
        elif hasattr(user, 'freelance_listing') and user.freelance_listing.is_active:
            user_skills = list(user.freelance_listing.skills.all())
        
        context['user_skills'] = user_skills
        
        # Prepare chart data
        context['chart_data'] = self._prepare_chart_data(
            city, state, zip_code, top_opportunities, trending_skills, user_opportunities
        )
        
        # Get personalized insights
        context['insights'] = self._generate_insights(user, city, state, zip_code, user_opportunities)
        
        # Get skill recommendations
        context['recommendations'] = self._get_recommendations(
            user, city, state, zip_code, user_skills
        )
        
        return context
    
    def _prepare_chart_data(self, city, state, zip_code, top_opportunities, trending_skills, user_opportunities):
        """Prepare data for Chart.js visualizations."""
        import json
        chart_data = {
            'top_opportunities': {
                'labels': json.dumps([opp.skill.name for opp in top_opportunities]),
                'demand_scores': json.dumps([float(opp.demand_score) for opp in top_opportunities]),
                'supply_scores': json.dumps([float(opp.supply_score) for opp in top_opportunities]),
                'opportunity_scores': json.dumps([float(opp.opportunity_score) for opp in top_opportunities]),
            },
            'trending_skills': {
                'labels': json.dumps([trend.skill.name for trend in trending_skills]),
                'demand_change': json.dumps([float(trend.demand_change_percent or 0) for trend in trending_skills]),
            },
            'user_opportunities': {
                'labels': json.dumps([opp.skill.name for opp in user_opportunities]),
                'demand_scores': json.dumps([float(opp.demand_score) for opp in user_opportunities]),
                'supply_scores': json.dumps([float(opp.supply_score) for opp in user_opportunities]),
            },
        }
        return chart_data
    
    def _generate_insights(self, user, city, state, zip_code, user_opportunities):
        """Generate personalized insights for the user."""
        insights = []
        
        if not user_opportunities:
            insights.append({
                'type': 'info',
                'message': 'Add skills to your profile to see personalized insights!',
            })
            return insights
        
        # High demand insight
        high_demand_opps = [opp for opp in user_opportunities if opp.market_status == 'high_opportunity']
        if high_demand_opps:
            top_skill = high_demand_opps[0]
            insights.append({
                'type': 'success',
                'message': f"Your {top_skill.skill.name} skills are in high demand! Consider raising your rates or taking on more projects.",
                'icon': '💰',
            })
        
        # Trending insight
        trending_demands = SkillDemand.objects.filter(
            city__iexact=city,
            state__iexact=state,
            demand_change_percent__gt=20,
        )
        if zip_code:
            trending_demands = trending_demands.filter(zip_code__startswith=zip_code[:5])
        
        user_skill_names = {opp.skill.name for opp in user_opportunities}
        for trend in trending_demands[:3]:
            if trend.skill.name not in user_skill_names:
                insights.append({
                    'type': 'info',
                    'message': f"Learn {trend.skill.name} - demand has increased by {trend.demand_change_percent:.0f}% in your area!",
                    'icon': '📈',
                })
                break
        
        # Skill swap opportunity
        from apps.accounts.modes_models import SkillSwapListing
        if hasattr(user, 'skill_swap_listing') and user.skill_swap_listing.is_active:
            swap_listings = SkillSwapListing.objects.filter(
                is_active=True,
                skills_wanted__in=[opp.skill for opp in user_opportunities[:5]]
            ).exclude(user=user).distinct()[:5]
            
            if swap_listings:
                insights.append({
                    'type': 'success',
                    'message': f"{swap_listings.count()} people near you want to learn what you offer! Check skill swap opportunities.",
                    'icon': '🤝',
                })
        
        return insights
    
    def _get_recommendations(self, user, city, state, zip_code, user_skills):
        """Get skill recommendations for the user."""
        recommendations = []
        
        # Get complementary skills
        user_skill_ids = {skill.id for skill in user_skills}
        
        # Get high opportunity skills that user doesn't have
        opportunities = SkillMarketOpportunity.objects.filter(
            city__iexact=city,
            state__iexact=state,
            market_status='high_opportunity',
        ).exclude(skill_id__in=user_skill_ids).order_by('-opportunity_score')[:5]
        
        for opp in opportunities:
            # Check if there are skill swap opportunities to learn
            from apps.accounts.modes_models import SkillSwapListing
            swap_opportunities = SkillSwapListing.objects.filter(
                is_active=True,
                skills_offered=opp.skill
            ).exclude(user=user).count()
            
            recommendations.append({
                'skill': opp.skill,
                'opportunity_score': opp.opportunity_score,
                'demand_score': opp.demand_score,
                'supply_score': opp.supply_score,
                'swap_opportunities': swap_opportunities,
                'message': f"High demand ({opp.demand_score:.0f}) with low supply ({opp.supply_score:.0f})",
            })
        
        return recommendations
