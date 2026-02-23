# Generated manually for unified job/booking system

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('providers', '0006_provider_profile_enhancements'),
        ('accounts', '0005_credit_system_enhancement'),
    ]

    operations = [
        # Add job acceptance preferences to ServiceProvider
        migrations.AddField(
            model_name='serviceprovider',
            name='accepts_paid_jobs',
            field=models.BooleanField(default=True, help_text='Accept paid job requests'),
        ),
        migrations.AddField(
            model_name='serviceprovider',
            name='accepts_credit_jobs',
            field=models.BooleanField(default=False, help_text='Accept credit-based skill swap jobs'),
        ),
        migrations.AddField(
            model_name='serviceprovider',
            name='accepts_barter',
            field=models.BooleanField(default=False, help_text='Accept barter proposals'),
        ),
        
        # Create UnifiedJob model
        migrations.CreateModel(
            name='UnifiedJob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_type', models.CharField(
                    choices=[
                        ('paid', 'Paid Job'),
                        ('credit', 'Credit-Based Swap'),
                        ('barter', 'Barter Proposal'),
                    ],
                    default='paid',
                    max_length=20
                )),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(help_text='Describe the work needed')),
                ('timeline', models.CharField(
                    choices=[
                        ('asap', 'As soon as possible'),
                        ('this_week', 'This week'),
                        ('next_week', 'Next week'),
                        ('this_month', 'This month'),
                        ('flexible', 'Flexible'),
                    ],
                    default='flexible',
                    max_length=20
                )),
                ('is_emergency', models.BooleanField(default=False)),
                ('service_address', models.CharField(blank=True, max_length=255)),
                ('service_city', models.CharField(blank=True, max_length=100)),
                ('service_state', models.CharField(blank=True, max_length=50)),
                ('service_zip', models.CharField(blank=True, max_length=20)),
                ('budget_min', models.DecimalField(
                    blank=True,
                    decimal_places=2,
                    help_text='Minimum budget (for paid jobs)',
                    max_digits=10,
                    null=True,
                    validators=[django.core.validators.MinValueValidator(0)]
                )),
                ('budget_max', models.DecimalField(
                    blank=True,
                    decimal_places=2,
                    help_text='Maximum budget (for paid jobs)',
                    max_digits=10,
                    null=True,
                    validators=[django.core.validators.MinValueValidator(0)]
                )),
                ('agreed_amount', models.DecimalField(
                    blank=True,
                    decimal_places=2,
                    help_text='Agreed payment amount',
                    max_digits=10,
                    null=True,
                    validators=[django.core.validators.MinValueValidator(0)]
                )),
                ('credits_requested', models.DecimalField(
                    blank=True,
                    decimal_places=2,
                    help_text='Credits requested (hours)',
                    max_digits=5,
                    null=True,
                    validators=[django.core.validators.MinValueValidator(0.5)]
                )),
                ('credits_agreed', models.DecimalField(
                    blank=True,
                    decimal_places=2,
                    help_text='Agreed credits (hours)',
                    max_digits=5,
                    null=True,
                    validators=[django.core.validators.MinValueValidator(0.5)]
                )),
                ('credits_in_escrow', models.DecimalField(
                    decimal_places=2,
                    default=0,
                    help_text='Credits held in escrow',
                    max_digits=10,
                    validators=[django.core.validators.MinValueValidator(0)]
                )),
                ('barter_offer', models.TextField(blank=True, help_text='What you offer in exchange (for barter proposals)')),
                ('barter_request', models.TextField(blank=True, help_text='What you want in exchange (for barter proposals)')),
                ('status', models.CharField(
                    choices=[
                        ('pending', 'Pending'),
                        ('proposed', 'Proposal Sent'),
                        ('accepted', 'Accepted'),
                        ('declined', 'Declined'),
                        ('in_progress', 'In Progress'),
                        ('completed', 'Completed'),
                        ('cancelled', 'Cancelled'),
                        ('disputed', 'Disputed'),
                    ],
                    default='pending',
                    max_length=20
                )),
                ('requester_confirmed', models.BooleanField(default=False)),
                ('provider_confirmed', models.BooleanField(default=False)),
                ('payment_processed', models.BooleanField(default=False)),
                ('payment_processed_at', models.DateTimeField(blank=True, null=True)),
                ('preferred_contact', models.CharField(
                    choices=[('email', 'Email'), ('phone', 'Phone'), ('either', 'Either')],
                    default='either',
                    max_length=20
                )),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('dispute_reason', models.TextField(blank=True)),
                ('dispute_resolved_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('accepted_at', models.DateTimeField(blank=True, null=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('cancelled_at', models.DateTimeField(blank=True, null=True)),
                ('dispute_resolved_by', models.ForeignKey(
                    blank=True,
                    help_text='Admin who resolved the dispute',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='unified_job_disputes_resolved',
                    to=settings.AUTH_USER_MODEL
                )),
                ('provider', models.ForeignKey(
                    blank=True,
                    help_text='User providing the service (set when accepted)',
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='jobs_provided',
                    to=settings.AUTH_USER_MODEL
                )),
                ('related_quote_request', models.ForeignKey(
                    blank=True,
                    help_text='Related quote request (if converted from quote)',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='unified_job',
                    to='providers.quoterequest'
                )),
                ('related_skill_swap_job', models.ForeignKey(
                    blank=True,
                    help_text='Related skill swap job (if converted)',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='unified_jobs',
                    to='accounts.skillswapjob'
                )),
                ('requester', models.ForeignKey(
                    help_text='User requesting the service',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='jobs_requested',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'Unified Job',
                'verbose_name_plural': 'Unified Jobs',
                'ordering': ['-created_at'],
            },
        ),
        
        # Create JobProposal model
        migrations.CreateModel(
            name='JobProposal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proposal_type', models.CharField(
                    choices=[
                        ('initial', 'Initial Proposal'),
                        ('counter', 'Counter Offer'),
                        ('accept', 'Acceptance'),
                        ('decline', 'Decline'),
                    ],
                    default='initial',
                    max_length=20
                )),
                ('status', models.CharField(
                    choices=[
                        ('pending', 'Pending'),
                        ('accepted', 'Accepted'),
                        ('declined', 'Declined'),
                        ('expired', 'Expired'),
                    ],
                    default='pending',
                    max_length=20
                )),
                ('message', models.TextField(help_text='Proposal message')),
                ('proposed_amount', models.DecimalField(
                    blank=True,
                    decimal_places=2,
                    help_text='Proposed payment amount',
                    max_digits=10,
                    null=True,
                    validators=[django.core.validators.MinValueValidator(0)]
                )),
                ('proposed_credits', models.DecimalField(
                    blank=True,
                    decimal_places=2,
                    help_text='Proposed credits (hours)',
                    max_digits=5,
                    null=True,
                    validators=[django.core.validators.MinValueValidator(0.5)]
                )),
                ('proposed_barter_offer', models.TextField(blank=True, help_text='Proposed barter offer')),
                ('proposed_barter_request', models.TextField(blank=True, help_text='Proposed barter request')),
                ('response_message', models.TextField(blank=True, help_text='Response to this proposal')),
                ('responded_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('expires_at', models.DateTimeField(blank=True, help_text='Proposal expiration date', null=True)),
                ('job', models.ForeignKey(
                    help_text='Job this proposal is for',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='proposals',
                    to='providers.unifiedjob'
                )),
                ('proposed_by', models.ForeignKey(
                    help_text='User making the proposal',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='job_proposals',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'Job Proposal',
                'verbose_name_plural': 'Job Proposals',
                'ordering': ['-created_at'],
            },
        ),
        
        # Create JobMessage model
        migrations.CreateModel(
            name='JobMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('job', models.ForeignKey(
                    help_text='Job this message belongs to',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='messages',
                    to='providers.unifiedjob'
                )),
                ('recipient', models.ForeignKey(
                    help_text='User who receives the message',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='job_messages_received',
                    to=settings.AUTH_USER_MODEL
                )),
                ('related_proposal', models.ForeignKey(
                    blank=True,
                    help_text='Related proposal (if applicable)',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='messages',
                    to='providers.jobproposal'
                )),
                ('sender', models.ForeignKey(
                    help_text='User who sent the message',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='job_messages_sent',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'Job Message',
                'verbose_name_plural': 'Job Messages',
                'ordering': ['created_at'],
            },
        ),
        
        # Add indexes
        migrations.AddIndex(
            model_name='unifiedjob',
            index=models.Index(fields=['requester', 'status', '-created_at'], name='providers_un_require_idx'),
        ),
        migrations.AddIndex(
            model_name='unifiedjob',
            index=models.Index(fields=['provider', 'status', '-created_at'], name='providers_un_provide_idx'),
        ),
        migrations.AddIndex(
            model_name='unifiedjob',
            index=models.Index(fields=['payment_type', 'status'], name='providers_un_payment_idx'),
        ),
        migrations.AddIndex(
            model_name='jobproposal',
            index=models.Index(fields=['job', 'status', '-created_at'], name='providers_jo_job_id_idx'),
        ),
        migrations.AddIndex(
            model_name='jobproposal',
            index=models.Index(fields=['proposed_by', 'status'], name='providers_jo_propose_idx'),
        ),
        migrations.AddIndex(
            model_name='jobmessage',
            index=models.Index(fields=['job', '-created_at'], name='providers_jo_job_id_2_idx'),
        ),
        migrations.AddIndex(
            model_name='jobmessage',
            index=models.Index(fields=['recipient', 'is_read', '-created_at'], name='providers_jo_recipie_idx'),
        ),
    ]
