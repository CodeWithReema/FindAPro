# Generated manually for skill analytics system

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('providers', '0008_rename_providers_jo_job_id_2_idx_providers_j_job_id_1dba54_idx_and_more'),
        ('accounts', '0005_credit_system_enhancement'),
    ]

    operations = [
        # Create SkillDemand model
        migrations.CreateModel(
            name='SkillDemand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(db_index=True, max_length=100)),
                ('state', models.CharField(db_index=True, max_length=50)),
                ('zip_code', models.CharField(blank=True, db_index=True, max_length=20)),
                ('radius_miles', models.IntegerField(
                    default=25,
                    help_text='Radius in miles for area calculation',
                    validators=[django.core.validators.MinValueValidator(1)]
                )),
                ('demand_score', models.DecimalField(
                    decimal_places=2,
                    default=0,
                    help_text='Calculated demand score (higher = more demand)',
                    max_digits=10
                )),
                ('job_requests_count', models.IntegerField(default=0, help_text='Count from job requests')),
                ('skill_swap_wants_count', models.IntegerField(default=0, help_text='Count from skill swap wants')),
                ('total_demand_signals', models.IntegerField(default=0, help_text='Total demand signals')),
                ('previous_demand_score', models.DecimalField(
                    blank=True,
                    decimal_places=2,
                    help_text='Previous period demand score for trend calculation',
                    max_digits=10,
                    null=True
                )),
                ('demand_change_percent', models.DecimalField(
                    blank=True,
                    decimal_places=2,
                    help_text='Percentage change in demand (positive = increasing)',
                    max_digits=5,
                    null=True
                )),
                ('period_start', models.DateTimeField(help_text='Start of analysis period')),
                ('period_end', models.DateTimeField(help_text='End of analysis period')),
                ('calculated_at', models.DateTimeField(auto_now_add=True, help_text='When this record was calculated')),
                ('skill', models.ForeignKey(
                    help_text='Skill being tracked',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='demand_records',
                    to='accounts.skill'
                )),
            ],
            options={
                'verbose_name': 'Skill Demand',
                'verbose_name_plural': 'Skill Demands',
                'ordering': ['-demand_score', '-calculated_at'],
            },
        ),
        
        # Create SkillSupply model
        migrations.CreateModel(
            name='SkillSupply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(db_index=True, max_length=100)),
                ('state', models.CharField(db_index=True, max_length=50)),
                ('zip_code', models.CharField(blank=True, db_index=True, max_length=20)),
                ('radius_miles', models.IntegerField(
                    default=25,
                    help_text='Radius in miles for area calculation',
                    validators=[django.core.validators.MinValueValidator(1)]
                )),
                ('supply_score', models.DecimalField(
                    decimal_places=2,
                    default=0,
                    help_text='Calculated supply score (higher = more supply)',
                    max_digits=10
                )),
                ('provider_count', models.IntegerField(default=0, help_text='Count from service providers')),
                ('skill_swap_offers_count', models.IntegerField(default=0, help_text='Count from skill swap offers')),
                ('freelance_listings_count', models.IntegerField(default=0, help_text='Count from freelance listings')),
                ('total_supply_signals', models.IntegerField(default=0, help_text='Total supply signals')),
                ('previous_supply_score', models.DecimalField(
                    blank=True,
                    decimal_places=2,
                    help_text='Previous period supply score for trend calculation',
                    max_digits=10,
                    null=True
                )),
                ('supply_change_percent', models.DecimalField(
                    blank=True,
                    decimal_places=2,
                    help_text='Percentage change in supply (positive = increasing)',
                    max_digits=5,
                    null=True
                )),
                ('period_start', models.DateTimeField(help_text='Start of analysis period')),
                ('period_end', models.DateTimeField(help_text='End of analysis period')),
                ('calculated_at', models.DateTimeField(auto_now_add=True, help_text='When this record was calculated')),
                ('skill', models.ForeignKey(
                    help_text='Skill being tracked',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='supply_records',
                    to='accounts.skill'
                )),
            ],
            options={
                'verbose_name': 'Skill Supply',
                'verbose_name_plural': 'Skill Supplies',
                'ordering': ['-supply_score', '-calculated_at'],
            },
        ),
        
        # Create SkillMarketOpportunity model
        migrations.CreateModel(
            name='SkillMarketOpportunity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(db_index=True, max_length=100)),
                ('state', models.CharField(db_index=True, max_length=50)),
                ('zip_code', models.CharField(blank=True, db_index=True, max_length=20)),
                ('demand_score', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('supply_score', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('opportunity_score', models.DecimalField(
                    decimal_places=2,
                    default=0,
                    help_text='Opportunity score (high demand, low supply = high opportunity)',
                    max_digits=10
                )),
                ('market_status', models.CharField(
                    choices=[
                        ('high_opportunity', 'High Opportunity (High Demand, Low Supply)'),
                        ('balanced', 'Balanced Market'),
                        ('oversupplied', 'Oversupplied (Low Demand, High Supply)'),
                        ('emerging', 'Emerging (Low Demand, Low Supply)'),
                    ],
                    default='balanced',
                    max_length=20
                )),
                ('period_start', models.DateTimeField()),
                ('period_end', models.DateTimeField()),
                ('calculated_at', models.DateTimeField(auto_now_add=True)),
                ('skill', models.ForeignKey(
                    help_text='Skill being analyzed',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='market_opportunities',
                    to='accounts.skill'
                )),
            ],
            options={
                'verbose_name': 'Skill Market Opportunity',
                'verbose_name_plural': 'Skill Market Opportunities',
                'ordering': ['-opportunity_score', '-calculated_at'],
            },
        ),
        
        # Add indexes
        migrations.AddIndex(
            model_name='skilldemand',
            index=models.Index(fields=['city', 'state', '-demand_score'], name='providers_sk_city_st_idx'),
        ),
        migrations.AddIndex(
            model_name='skilldemand',
            index=models.Index(fields=['skill', 'city', 'state', '-calculated_at'], name='providers_sk_skill_c_idx'),
        ),
        migrations.AddIndex(
            model_name='skilldemand',
            index=models.Index(fields=['-demand_score', '-calculated_at'], name='providers_sk_demand__idx'),
        ),
        migrations.AddIndex(
            model_name='skillsupply',
            index=models.Index(fields=['city', 'state', '-supply_score'], name='providers_sk_city_st_2_idx'),
        ),
        migrations.AddIndex(
            model_name='skillsupply',
            index=models.Index(fields=['skill', 'city', 'state', '-calculated_at'], name='providers_sk_skill_c_2_idx'),
        ),
        migrations.AddIndex(
            model_name='skillsupply',
            index=models.Index(fields=['-supply_score', '-calculated_at'], name='providers_sk_supply_idx'),
        ),
        migrations.AddIndex(
            model_name='skillmarketopportunity',
            index=models.Index(fields=['city', 'state', '-opportunity_score'], name='providers_sk_city_st_3_idx'),
        ),
        migrations.AddIndex(
            model_name='skillmarketopportunity',
            index=models.Index(fields=['market_status', '-opportunity_score'], name='providers_sk_market__idx'),
        ),
        migrations.AddIndex(
            model_name='skillmarketopportunity',
            index=models.Index(fields=['skill', 'city', 'state', '-calculated_at'], name='providers_sk_skill_c_3_idx'),
        ),
        
        # Add unique constraints
        migrations.AddConstraint(
            model_name='skilldemand',
            constraint=models.UniqueConstraint(
                fields=['skill', 'city', 'state', 'zip_code', 'period_start', 'period_end'],
                name='unique_skill_demand_period'
            ),
        ),
        migrations.AddConstraint(
            model_name='skillsupply',
            constraint=models.UniqueConstraint(
                fields=['skill', 'city', 'state', 'zip_code', 'period_start', 'period_end'],
                name='unique_skill_supply_period'
            ),
        ),
        migrations.AddConstraint(
            model_name='skillmarketopportunity',
            constraint=models.UniqueConstraint(
                fields=['skill', 'city', 'state', 'zip_code', 'period_start', 'period_end'],
                name='unique_skill_opportunity_period'
            ),
        ),
    ]
