# Generated manually for smart matching system

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_multimode_profiles'),
    ]

    operations = [
        # Create Match model
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('match_type', models.CharField(
                    choices=[
                        ('skill_swap', 'Skill Swap'),
                        ('freelance_collab', 'Freelance Collaboration'),
                        ('both', 'Both'),
                    ],
                    default='skill_swap',
                    max_length=20
                )),
                ('compatibility_score', models.DecimalField(
                    decimal_places=2,
                    help_text='Compatibility score (0-100)',
                    max_digits=5,
                    validators=[
                        django.core.validators.MinValueValidator(0),
                        django.core.validators.MaxValueValidator(100)
                    ]
                )),
                ('skill_overlap_percentage', models.DecimalField(
                    decimal_places=2,
                    default=0,
                    help_text='Percentage of skills that overlap',
                    max_digits=5
                )),
                ('matching_skills', models.JSONField(default=list, help_text='List of skills that match')),
                ('geographic_proximity_score', models.DecimalField(
                    decimal_places=2,
                    default=0,
                    help_text='Geographic proximity score',
                    max_digits=5
                )),
                ('reputation_score', models.DecimalField(
                    decimal_places=2,
                    default=0,
                    help_text='Combined reputation/rating score',
                    max_digits=5
                )),
                ('availability_score', models.DecimalField(
                    decimal_places=2,
                    default=0,
                    help_text='Availability alignment score',
                    max_digits=5
                )),
                ('status', models.CharField(
                    choices=[
                        ('pending', 'Pending'),
                        ('viewed', 'Viewed'),
                        ('interested', 'Interested'),
                        ('connected', 'Connected'),
                        ('not_interested', 'Not Interested'),
                        ('expired', 'Expired'),
                    ],
                    default='pending',
                    max_length=20
                )),
                ('user_a_interested', models.BooleanField(default=False)),
                ('user_b_interested', models.BooleanField(default=False)),
                ('user_a_not_interested', models.BooleanField(default=False)),
                ('user_b_not_interested', models.BooleanField(default=False)),
                ('connected_at', models.DateTimeField(blank=True, null=True)),
                ('last_viewed_a', models.DateTimeField(blank=True, null=True)),
                ('last_viewed_b', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user_a', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='matches_as_a',
                    to=settings.AUTH_USER_MODEL
                )),
                ('user_b', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='matches_as_b',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'Match',
                'verbose_name_plural': 'Matches',
                'ordering': ['-compatibility_score', '-created_at'],
            },
        ),
        
        # Create MatchHistory model
        migrations.CreateModel(
            name='MatchHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(
                    choices=[
                        ('suggested', 'Suggested'),
                        ('viewed', 'Viewed'),
                        ('interested', 'Interested'),
                        ('not_interested', 'Not Interested'),
                        ('connected', 'Connected'),
                    ],
                    max_length=20
                )),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('match', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='history_records',
                    to='accounts.match'
                )),
                ('matched_user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='matched_by_history',
                    to=settings.AUTH_USER_MODEL
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='match_history',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'Match History',
                'verbose_name_plural': 'Match Histories',
                'ordering': ['-created_at'],
            },
        ),
        
        # Add indexes
        migrations.AddIndex(
            model_name='match',
            index=models.Index(fields=['user_a', 'status'], name='accounts_ma_user_a__idx'),
        ),
        migrations.AddIndex(
            model_name='match',
            index=models.Index(fields=['user_b', 'status'], name='accounts_ma_user_b__idx'),
        ),
        migrations.AddIndex(
            model_name='matchhistory',
            index=models.Index(fields=['user', 'action'], name='accounts_ma_user_id_idx'),
        ),
        
        # Add unique constraints
        migrations.AlterUniqueTogether(
            name='match',
            unique_together={('user_a', 'user_b', 'match_type')},
        ),
        migrations.AlterUniqueTogether(
            name='matchhistory',
            unique_together={('user', 'matched_user', 'action')},
        ),
    ]
