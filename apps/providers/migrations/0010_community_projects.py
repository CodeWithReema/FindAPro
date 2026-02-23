# Generated manually for community project board

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('providers', '0009_skill_analytics'),
        ('accounts', '0005_credit_system_enhancement'),
    ]

    operations = [
        # Create CommunityProject model
        migrations.CreateModel(
            name='CommunityProject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(help_text='Detailed project description')),
                ('project_type', models.CharField(
                    choices=[
                        ('community', 'Community Project'),
                        ('creative', 'Creative Collaboration'),
                        ('business', 'Business Venture'),
                        ('learning', 'Learning Project'),
                    ],
                    default='community',
                    max_length=20
                )),
                ('status', models.CharField(
                    choices=[
                        ('draft', 'Draft'),
                        ('recruiting', 'Recruiting Team Members'),
                        ('in_progress', 'In Progress'),
                        ('completed', 'Completed'),
                        ('cancelled', 'Cancelled'),
                    ],
                    default='draft',
                    max_length=20
                )),
                ('start_date', models.DateField(blank=True, help_text='Project start date', null=True)),
                ('end_date', models.DateField(blank=True, help_text='Expected completion date', null=True)),
                ('timeline_description', models.CharField(blank=True, help_text='Timeline description (e.g., "3-6 months", "Ongoing")', max_length=255)),
                ('location_city', models.CharField(max_length=100)),
                ('location_state', models.CharField(max_length=50)),
                ('location_address', models.CharField(blank=True, max_length=255)),
                ('location_zip', models.CharField(blank=True, max_length=20)),
                ('is_remote_friendly', models.BooleanField(default=False, help_text='Can team members work remotely?')),
                ('compensation_type', models.CharField(
                    choices=[
                        ('paid', 'Paid'),
                        ('credits', 'Credits'),
                        ('volunteer', 'Volunteer'),
                        ('mixed', 'Mixed'),
                    ],
                    default='volunteer',
                    max_length=20
                )),
                ('budget_total', models.DecimalField(
                    blank=True,
                    decimal_places=2,
                    help_text='Total project budget (if applicable)',
                    max_digits=10,
                    null=True
                )),
                ('featured_image', models.ImageField(blank=True, help_text='Main project image', null=True, upload_to='projects/featured/')),
                ('is_featured', models.BooleanField(default=False, help_text='Featured community project')),
                ('view_count', models.IntegerField(default=0)),
                ('application_count', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('creator', models.ForeignKey(
                    help_text='User who created the project',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='created_projects',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'Community Project',
                'verbose_name_plural': 'Community Projects',
                'ordering': ['-created_at'],
            },
        ),
        
        # Create ProjectRole model
        migrations.CreateModel(
            name='ProjectRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Role title (e.g., "Lead Electrician")', max_length=200)),
                ('description', models.TextField(help_text='Role description and responsibilities')),
                ('time_commitment_hours', models.DecimalField(
                    blank=True,
                    decimal_places=2,
                    help_text='Hours per week/month required',
                    max_digits=5,
                    null=True,
                    validators=[django.core.validators.MinValueValidator(0)]
                )),
                ('time_commitment_description', models.CharField(blank=True, help_text='Time commitment description (e.g., "10 hours/week", "Full-time")', max_length=255)),
                ('experience_level', models.CharField(
                    choices=[
                        ('beginner', 'Beginner'),
                        ('intermediate', 'Intermediate'),
                        ('advanced', 'Advanced'),
                        ('expert', 'Expert'),
                    ],
                    default='intermediate',
                    max_length=20
                )),
                ('compensation_type', models.CharField(
                    choices=[
                        ('paid', 'Paid'),
                        ('credits', 'Credits'),
                        ('volunteer', 'Volunteer'),
                    ],
                    default='volunteer',
                    max_length=20
                )),
                ('compensation_amount', models.DecimalField(
                    blank=True,
                    decimal_places=2,
                    help_text='Compensation amount (pay rate, credits, etc.)',
                    max_digits=10,
                    null=True
                )),
                ('compensation_description', models.CharField(blank=True, help_text='Compensation description', max_length=255)),
                ('status', models.CharField(
                    choices=[
                        ('open', 'Open - Accepting Applications'),
                        ('filled', 'Filled'),
                        ('closed', 'Closed - No Longer Needed'),
                    ],
                    default='open',
                    max_length=20
                )),
                ('filled_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('filled_by', models.ForeignKey(
                    blank=True,
                    help_text='User who filled this role',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='filled_roles',
                    to=settings.AUTH_USER_MODEL
                )),
                ('project', models.ForeignKey(
                    help_text='Project this role belongs to',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='roles',
                    to='providers.communityproject'
                )),
                ('skill_required', models.ForeignKey(
                    blank=True,
                    help_text='Primary skill required for this role',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='project_roles',
                    to='accounts.skill'
                )),
            ],
            options={
                'verbose_name': 'Project Role',
                'verbose_name_plural': 'Project Roles',
                'ordering': ['created_at'],
            },
        ),
        
        # Create ProjectApplication model
        migrations.CreateModel(
            name='ProjectApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cover_letter', models.TextField(help_text="Why you're interested and qualified")),
                ('relevant_experience', models.TextField(blank=True, help_text='Relevant experience and portfolio links')),
                ('status', models.CharField(
                    choices=[
                        ('pending', 'Pending Review'),
                        ('accepted', 'Accepted'),
                        ('declined', 'Declined'),
                        ('withdrawn', 'Withdrawn'),
                    ],
                    default='pending',
                    max_length=20
                )),
                ('review_notes', models.TextField(blank=True, help_text='Internal review notes')),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('applicant', models.ForeignKey(
                    help_text='User applying for the role',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='project_applications',
                    to=settings.AUTH_USER_MODEL
                )),
                ('reviewed_by', models.ForeignKey(
                    blank=True,
                    help_text='Project creator who reviewed this application',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='reviewed_applications',
                    to=settings.AUTH_USER_MODEL
                )),
                ('role', models.ForeignKey(
                    help_text='Role being applied for',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='applications',
                    to='providers.projectrole'
                )),
            ],
            options={
                'verbose_name': 'Project Application',
                'verbose_name_plural': 'Project Applications',
                'ordering': ['-created_at'],
            },
        ),
        
        # Create ProjectMember model
        migrations.CreateModel(
            name='ProjectMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role_title', models.CharField(blank=True, help_text='Custom role title (if different from role.title)', max_length=200)),
                ('is_creator', models.BooleanField(default=False, help_text='Is this the project creator?')),
                ('is_lead', models.BooleanField(default=False, help_text='Is this a project lead?')),
                ('status', models.CharField(
                    choices=[
                        ('active', 'Active'),
                        ('inactive', 'Inactive'),
                        ('removed', 'Removed'),
                    ],
                    default='active',
                    max_length=20
                )),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('left_at', models.DateTimeField(blank=True, null=True)),
                ('project', models.ForeignKey(
                    help_text='Project this member belongs to',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='members',
                    to='providers.communityproject'
                )),
                ('role', models.ForeignKey(
                    blank=True,
                    help_text='Role this member fills',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='members',
                    to='providers.projectrole'
                )),
                ('user', models.ForeignKey(
                    help_text='Team member',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='project_memberships',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'Project Member',
                'verbose_name_plural': 'Project Members',
            },
        ),
        
        # Create ProjectMilestone model
        migrations.CreateModel(
            name='ProjectMilestone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('due_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(
                    choices=[
                        ('not_started', 'Not Started'),
                        ('in_progress', 'In Progress'),
                        ('completed', 'Completed'),
                        ('blocked', 'Blocked'),
                    ],
                    default='not_started',
                    max_length=20
                )),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_to', models.ManyToManyField(blank=True, related_name='assigned_milestones', to=settings.AUTH_USER_MODEL)),
                ('completed_by', models.ForeignKey(
                    blank=True,
                    help_text='User who marked milestone as completed',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='completed_milestones',
                    to=settings.AUTH_USER_MODEL
                )),
                ('project', models.ForeignKey(
                    help_text='Project this milestone belongs to',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='milestones',
                    to='providers.communityproject'
                )),
            ],
            options={
                'verbose_name': 'Project Milestone',
                'verbose_name_plural': 'Project Milestones',
                'ordering': ['due_date', 'created_at'],
            },
        ),
        
        # Create ProjectFile model
        migrations.CreateModel(
            name='ProjectFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='projects/files/')),
                ('file_type', models.CharField(
                    choices=[
                        ('document', 'Document'),
                        ('image', 'Image'),
                        ('design', 'Design File'),
                        ('plan', 'Plan/Blueprint'),
                        ('other', 'Other'),
                    ],
                    default='document',
                    max_length=20
                )),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('milestone', models.ForeignKey(
                    blank=True,
                    help_text='Related milestone (if applicable)',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='files',
                    to='providers.projectmilestone'
                )),
                ('project', models.ForeignKey(
                    help_text='Project this file belongs to',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='files',
                    to='providers.communityproject'
                )),
                ('uploaded_by', models.ForeignKey(
                    help_text='User who uploaded the file',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='uploaded_project_files',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'Project File',
                'verbose_name_plural': 'Project Files',
                'ordering': ['-created_at'],
            },
        ),
        
        # Create ProjectMessage model
        migrations.CreateModel(
            name='ProjectMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('is_pinned', models.BooleanField(default=False, help_text='Pin important messages')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('milestone', models.ForeignKey(
                    blank=True,
                    help_text='Related milestone (if applicable)',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='messages',
                    to='providers.projectmilestone'
                )),
                ('project', models.ForeignKey(
                    help_text='Project this message belongs to',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='messages',
                    to='providers.communityproject'
                )),
                ('sender', models.ForeignKey(
                    help_text='User who sent the message',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='project_messages_sent',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'Project Message',
                'verbose_name_plural': 'Project Messages',
                'ordering': ['-is_pinned', 'created_at'],
            },
        ),
        
        # Create UserBadge model
        migrations.CreateModel(
            name='UserBadge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('badge_type', models.CharField(
                    choices=[
                        ('community_builder', 'Community Builder'),
                        ('collaborator', 'Collaborator'),
                        ('project_leader', 'Project Leader'),
                        ('skill_sharer', 'Skill Sharer'),
                        ('mentor', 'Mentor'),
                        ('volunteer', 'Volunteer'),
                    ],
                    help_text='Category of badge',
                    max_length=20
                )),
                ('description', models.TextField(help_text='What this badge represents')),
                ('icon', models.CharField(blank=True, help_text='Icon class or emoji (e.g., 🏆, fa-trophy)', max_length=50)),
                ('image', models.ImageField(blank=True, help_text='Badge image', null=True, upload_to='badges/')),
                ('criteria', models.TextField(help_text='How to earn this badge (e.g., "Complete 5 community projects")')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'User Badge',
                'verbose_name_plural': 'User Badges',
                'ordering': ['badge_type', 'name'],
            },
        ),
        
        # Create UserBadgeAward model
        migrations.CreateModel(
            name='UserBadgeAward',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('awarded_at', models.DateTimeField(auto_now_add=True)),
                ('notes', models.TextField(blank=True, help_text='Additional notes about the award')),
                ('awarded_for_project', models.ForeignKey(
                    blank=True,
                    help_text='Project that triggered this badge (if applicable)',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='badge_awards',
                    to='providers.communityproject'
                )),
                ('badge', models.ForeignKey(
                    help_text='Badge that was awarded',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='awards',
                    to='providers.userbadge'
                )),
                ('user', models.ForeignKey(
                    help_text='User who earned the badge',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='badges_awarded',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'Badge Award',
                'verbose_name_plural': 'Badge Awards',
                'ordering': ['-awarded_at'],
            },
        ),
        
        # Add indexes
        migrations.AddIndex(
            model_name='communityproject',
            index=models.Index(fields=['status', '-created_at'], name='providers_co_status_idx'),
        ),
        migrations.AddIndex(
            model_name='communityproject',
            index=models.Index(fields=['project_type', 'status'], name='providers_co_project_idx'),
        ),
        migrations.AddIndex(
            model_name='communityproject',
            index=models.Index(fields=['location_city', 'location_state', '-created_at'], name='providers_co_locatio_idx'),
        ),
        migrations.AddIndex(
            model_name='communityproject',
            index=models.Index(fields=['is_featured', '-created_at'], name='providers_co_is_feat_idx'),
        ),
        migrations.AddIndex(
            model_name='projectapplication',
            index=models.Index(fields=['role', 'status', '-created_at'], name='providers_pr_role_id_idx'),
        ),
        migrations.AddIndex(
            model_name='projectapplication',
            index=models.Index(fields=['applicant', 'status'], name='providers_pr_applica_idx'),
        ),
        migrations.AddIndex(
            model_name='projectmember',
            index=models.Index(fields=['project', 'status'], name='providers_pr_project_idx'),
        ),
        migrations.AddIndex(
            model_name='projectmember',
            index=models.Index(fields=['user', 'status'], name='providers_pr_user_id_idx'),
        ),
        migrations.AddIndex(
            model_name='projectmessage',
            index=models.Index(fields=['project', '-created_at'], name='providers_pr_project_2_idx'),
        ),
        migrations.AddIndex(
            model_name='userbadgeaward',
            index=models.Index(fields=['user', '-awarded_at'], name='providers_us_user_id_idx'),
        ),
        
        # Add unique constraints
        migrations.AddConstraint(
            model_name='projectapplication',
            constraint=models.UniqueConstraint(fields=['role', 'applicant'], name='unique_role_application'),
        ),
        migrations.AddConstraint(
            model_name='projectmember',
            constraint=models.UniqueConstraint(fields=['project', 'user'], name='unique_project_member'),
        ),
        migrations.AddConstraint(
            model_name='userbadgeaward',
            constraint=models.UniqueConstraint(fields=['user', 'badge'], name='unique_user_badge'),
        ),
        
        # Add many-to-many relationships
        migrations.AddField(
            model_name='projectrole',
            name='skills_preferred',
            field=models.ManyToManyField(blank=True, related_name='preferred_roles', to='accounts.skill'),
        ),
    ]
