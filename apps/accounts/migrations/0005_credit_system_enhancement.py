# Generated manually for credit system enhancement

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_remove_match_accounts_ma_user_a__idx_and_more'),
    ]

    operations = [
        # Create SkillSwapJob model
        migrations.CreateModel(
            name='SkillSwapJob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('hours_required', models.DecimalField(
                    decimal_places=2,
                    help_text='Number of hours required (1 hour = 1 credit)',
                    max_digits=5,
                    validators=[django.core.validators.MinValueValidator(0.5)]
                )),
                ('status', models.CharField(
                    choices=[
                        ('posted', 'Posted'),
                        ('accepted', 'Accepted'),
                        ('in_progress', 'In Progress'),
                        ('completed', 'Completed'),
                        ('cancelled', 'Cancelled'),
                        ('disputed', 'Disputed'),
                    ],
                    default='posted',
                    max_length=20
                )),
                ('posted_at', models.DateTimeField(auto_now_add=True)),
                ('accepted_at', models.DateTimeField(blank=True, null=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('cancelled_at', models.DateTimeField(blank=True, null=True)),
                ('requester_confirmed', models.BooleanField(default=False)),
                ('provider_confirmed', models.BooleanField(default=False)),
                ('credits_in_escrow', models.DecimalField(
                    decimal_places=2,
                    default=0,
                    help_text='Credits held in escrow until completion',
                    max_digits=10,
                    validators=[django.core.validators.MinValueValidator(0)]
                )),
                ('dispute_reason', models.TextField(blank=True)),
                ('dispute_resolved_at', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('dispute_resolved_by', models.ForeignKey(
                    blank=True,
                    help_text='Admin who resolved the dispute',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='disputes_resolved',
                    to=settings.AUTH_USER_MODEL
                )),
                ('provider', models.ForeignKey(
                    blank=True,
                    help_text='User providing the service',
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='swap_jobs_provided',
                    to=settings.AUTH_USER_MODEL
                )),
                ('requester', models.ForeignKey(
                    help_text='User requesting the service',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='swap_jobs_requested',
                    to=settings.AUTH_USER_MODEL
                )),
                ('skill_needed', models.ForeignKey(
                    blank=True,
                    help_text='Skill needed for this job',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='swap_jobs',
                    to='accounts.skill'
                )),
            ],
            options={
                'verbose_name': 'Skill Swap Job',
                'verbose_name_plural': 'Skill Swap Jobs',
                'ordering': ['-posted_at'],
            },
        ),
        
        # Add indexes for SkillSwapJob
        migrations.AddIndex(
            model_name='skillswapjob',
            index=models.Index(fields=['requester', 'status'], name='accounts_sk_require_idx'),
        ),
        migrations.AddIndex(
            model_name='skillswapjob',
            index=models.Index(fields=['provider', 'status'], name='accounts_sk_provide_idx'),
        ),
        
        # Update SkillCredit model - add new fields
        migrations.AddField(
            model_name='skillcredit',
            name='job',
            field=models.ForeignKey(
                blank=True,
                help_text='Associated skill swap job',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='credit_transactions',
                to='accounts.skillswapjob'
            ),
        ),
        migrations.AddField(
            model_name='skillcredit',
            name='admin_notes',
            field=models.TextField(blank=True, help_text='Admin notes for adjustments or disputes'),
        ),
        migrations.AddField(
            model_name='skillcredit',
            name='expires_at',
            field=models.DateTimeField(blank=True, help_text='Credit expiration date (if applicable)', null=True),
        ),
        
        # Make from_user nullable for system transactions
        migrations.AlterField(
            model_name='skillcredit',
            name='from_user',
            field=models.ForeignKey(
                blank=True,
                help_text='User who provided the service (null for system transactions)',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='credits_given',
                to=settings.AUTH_USER_MODEL
            ),
        ),
        
        # Make swap_date nullable
        migrations.AlterField(
            model_name='skillcredit',
            name='swap_date',
            field=models.DateField(blank=True, help_text='Date when the swap occurred', null=True),
        ),
        
        # Update transaction_type choices (add new types)
        migrations.AlterField(
            model_name='skillcredit',
            name='transaction_type',
            field=models.CharField(
                choices=[
                    ('earned', 'Earned'),
                    ('spent', 'Spent'),
                    ('bonus', 'Bonus'),
                    ('adjustment', 'Adjustment'),
                    ('refund', 'Refund'),
                    ('escrow_hold', 'Escrow Hold'),
                    ('escrow_release', 'Escrow Release'),
                ],
                max_length=20
            ),
        ),
        
        # Update status choices
        migrations.AlterField(
            model_name='skillcredit',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('approved', 'Approved'),
                    ('rejected', 'Rejected'),
                    ('cancelled', 'Cancelled'),
                ],
                default='pending',
                max_length=20
            ),
        ),
        
        # Update ordering
        migrations.AlterModelOptions(
            name='skillcredit',
            options={
                'ordering': ['-created_at'],
                'verbose_name': 'Skill Credit',
                'verbose_name_plural': 'Skill Credits',
            },
        ),
        
        # Add indexes for SkillCredit
        migrations.AddIndex(
            model_name='skillcredit',
            index=models.Index(fields=['to_user', 'status', '-created_at'], name='accounts_sk_to_user_idx'),
        ),
        migrations.AddIndex(
            model_name='skillcredit',
            index=models.Index(fields=['transaction_type', 'status'], name='accounts_sk_transac_idx'),
        ),
    ]
