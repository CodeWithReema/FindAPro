"""
Skill supply and demand analytics models.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal


class SkillDemand(models.Model):
    """Track demand for skills by geographic area."""
    
    skill = models.ForeignKey(
        'accounts.Skill',
        on_delete=models.CASCADE,
        related_name='demand_records',
        help_text='Skill being tracked'
    )
    
    # Geographic area
    city = models.CharField(max_length=100, db_index=True)
    state = models.CharField(max_length=50, db_index=True)
    zip_code = models.CharField(max_length=20, blank=True, db_index=True)
    radius_miles = models.IntegerField(
        default=25,
        help_text='Radius in miles for area calculation',
        validators=[MinValueValidator(1)]
    )
    
    # Demand metrics
    demand_score = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Calculated demand score (higher = more demand)'
    )
    
    # Source breakdown
    job_requests_count = models.IntegerField(default=0, help_text='Count from job requests')
    skill_swap_wants_count = models.IntegerField(default=0, help_text='Count from skill swap wants')
    total_demand_signals = models.IntegerField(default=0, help_text='Total demand signals')
    
    # Trend tracking
    previous_demand_score = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Previous period demand score for trend calculation'
    )
    demand_change_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Percentage change in demand (positive = increasing)'
    )
    
    # Time period
    period_start = models.DateTimeField(help_text='Start of analysis period')
    period_end = models.DateTimeField(help_text='End of analysis period')
    calculated_at = models.DateTimeField(auto_now_add=True, help_text='When this record was calculated')
    
    class Meta:
        verbose_name = 'Skill Demand'
        verbose_name_plural = 'Skill Demands'
        ordering = ['-demand_score', '-calculated_at']
        indexes = [
            models.Index(fields=['city', 'state', '-demand_score']),
            models.Index(fields=['skill', 'city', 'state', '-calculated_at']),
            models.Index(fields=['-demand_score', '-calculated_at']),
        ]
        unique_together = [
            ['skill', 'city', 'state', 'zip_code', 'period_start', 'period_end']
        ]
    
    def __str__(self):
        return f"{self.skill.name} - {self.city}, {self.state} (Score: {self.demand_score})"
    
    @property
    def is_trending_up(self):
        """Check if demand is trending upward."""
        return self.demand_change_percent and self.demand_change_percent > 0
    
    @property
    def trend_direction(self):
        """Get trend direction as string."""
        if not self.demand_change_percent:
            return 'stable'
        if self.demand_change_percent > 10:
            return 'hot'
        elif self.demand_change_percent > 0:
            return 'rising'
        elif self.demand_change_percent < -10:
            return 'cooling'
        elif self.demand_change_percent < 0:
            return 'declining'
        return 'stable'


class SkillSupply(models.Model):
    """Track supply of skills by geographic area."""
    
    skill = models.ForeignKey(
        'accounts.Skill',
        on_delete=models.CASCADE,
        related_name='supply_records',
        help_text='Skill being tracked'
    )
    
    # Geographic area
    city = models.CharField(max_length=100, db_index=True)
    state = models.CharField(max_length=50, db_index=True)
    zip_code = models.CharField(max_length=20, blank=True, db_index=True)
    radius_miles = models.IntegerField(
        default=25,
        help_text='Radius in miles for area calculation',
        validators=[MinValueValidator(1)]
    )
    
    # Supply metrics
    supply_score = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Calculated supply score (higher = more supply)'
    )
    
    # Source breakdown
    provider_count = models.IntegerField(default=0, help_text='Count from service providers')
    skill_swap_offers_count = models.IntegerField(default=0, help_text='Count from skill swap offers')
    freelance_listings_count = models.IntegerField(default=0, help_text='Count from freelance listings')
    total_supply_signals = models.IntegerField(default=0, help_text='Total supply signals')
    
    # Trend tracking
    previous_supply_score = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Previous period supply score for trend calculation'
    )
    supply_change_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Percentage change in supply (positive = increasing)'
    )
    
    # Time period
    period_start = models.DateTimeField(help_text='Start of analysis period')
    period_end = models.DateTimeField(help_text='End of analysis period')
    calculated_at = models.DateTimeField(auto_now_add=True, help_text='When this record was calculated')
    
    class Meta:
        verbose_name = 'Skill Supply'
        verbose_name_plural = 'Skill Supplies'
        ordering = ['-supply_score', '-calculated_at']
        indexes = [
            models.Index(fields=['city', 'state', '-supply_score']),
            models.Index(fields=['skill', 'city', 'state', '-calculated_at']),
            models.Index(fields=['-supply_score', '-calculated_at']),
        ]
        unique_together = [
            ['skill', 'city', 'state', 'zip_code', 'period_start', 'period_end']
        ]
    
    def __str__(self):
        return f"{self.skill.name} - {self.city}, {self.state} (Score: {self.supply_score})"
    
    @property
    def is_trending_up(self):
        """Check if supply is trending upward."""
        return self.supply_change_percent and self.supply_change_percent > 0


class SkillMarketOpportunity(models.Model):
    """Aggregated view of skill market opportunities (demand vs supply)."""
    
    skill = models.ForeignKey(
        'accounts.Skill',
        on_delete=models.CASCADE,
        related_name='market_opportunities',
        help_text='Skill being analyzed'
    )
    
    # Geographic area
    city = models.CharField(max_length=100, db_index=True)
    state = models.CharField(max_length=50, db_index=True)
    zip_code = models.CharField(max_length=20, blank=True, db_index=True)
    
    # Market metrics
    demand_score = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    supply_score = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    opportunity_score = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Opportunity score (high demand, low supply = high opportunity)'
    )
    
    # Market status
    market_status = models.CharField(
        max_length=20,
        choices=[
            ('high_opportunity', 'High Opportunity (High Demand, Low Supply)'),
            ('balanced', 'Balanced Market'),
            ('oversupplied', 'Oversupplied (Low Demand, High Supply)'),
            ('emerging', 'Emerging (Low Demand, Low Supply)'),
        ],
        default='balanced'
    )
    
    # Time period
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    calculated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Skill Market Opportunity'
        verbose_name_plural = 'Skill Market Opportunities'
        ordering = ['-opportunity_score', '-calculated_at']
        indexes = [
            models.Index(fields=['city', 'state', '-opportunity_score']),
            models.Index(fields=['market_status', '-opportunity_score']),
            models.Index(fields=['skill', 'city', 'state', '-calculated_at']),
        ]
        unique_together = [
            ['skill', 'city', 'state', 'zip_code', 'period_start', 'period_end']
        ]
    
    def __str__(self):
        return f"{self.skill.name} - {self.city}, {self.state} ({self.get_market_status_display()})"
    
    @property
    def demand_supply_ratio(self):
        """Calculate demand to supply ratio."""
        if self.supply_score == 0:
            return Decimal('999.99')  # Infinite demand, no supply
        return self.demand_score / self.supply_score
