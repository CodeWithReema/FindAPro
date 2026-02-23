# Generated manually for multi-mode profile system

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        # Add mode fields to CustomUser
        migrations.AddField(
            model_name='customuser',
            name='is_freelancer_active',
            field=models.BooleanField(default=False, help_text='Freelance mode is active'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_skill_swap_active',
            field=models.BooleanField(default=False, help_text='Skill swap mode is active'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='active_mode',
            field=models.CharField(
                blank=True,
                choices=[
                    ('provider', 'Service Provider'),
                    ('freelance', 'Freelance'),
                    ('skill_swap', 'Skill Swap'),
                ],
                default='provider',
                help_text='Currently active mode for UI context',
                max_length=20
            ),
        ),
        
        # Create Skill model
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('category', models.CharField(
                    choices=[
                        ('design', 'Design'),
                        ('development', 'Development'),
                        ('marketing', 'Marketing'),
                        ('writing', 'Writing'),
                        ('business', 'Business'),
                        ('technical', 'Technical'),
                        ('creative', 'Creative'),
                        ('other', 'Other'),
                    ],
                    default='other',
                    max_length=50
                )),
                ('description', models.TextField(blank=True)),
                ('icon', models.CharField(blank=True, help_text='Icon class or emoji', max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Skill',
                'verbose_name_plural': 'Skills',
                'ordering': ['category', 'name'],
            },
        ),
        
        # Create FreelanceListing model
        migrations.CreateModel(
            name='FreelanceListing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Professional title or tagline', max_length=200)),
                ('bio', models.TextField(help_text='Professional bio/description')),
                ('headline', models.CharField(blank=True, help_text='Short headline', max_length=255)),
                ('expertise_tags', models.CharField(blank=True, help_text='Comma-separated additional tags', max_length=500)),
                ('pricing_type', models.CharField(
                    choices=[
                        ('hourly', 'Hourly Rate'),
                        ('project', 'Project-Based'),
                        ('both', 'Both'),
                    ],
                    default='both',
                    max_length=20
                )),
                ('hourly_rate', models.DecimalField(
                    blank=True,
                    decimal_places=2,
                    help_text='Hourly rate in USD',
                    max_digits=10,
                    null=True,
                    validators=[django.core.validators.MinValueValidator(0)]
                )),
                ('project_rate_min', models.DecimalField(
                    blank=True,
                    decimal_places=2,
                    help_text='Minimum project rate',
                    max_digits=10,
                    null=True,
                    validators=[django.core.validators.MinValueValidator(0)]
                )),
                ('project_rate_max', models.DecimalField(
                    blank=True,
                    decimal_places=2,
                    help_text='Maximum project rate',
                    max_digits=10,
                    null=True,
                    validators=[django.core.validators.MinValueValidator(0)]
                )),
                ('currency', models.CharField(default='USD', max_length=3)),
                ('portfolio_url', models.URLField(blank=True, help_text='Link to portfolio website')),
                ('github_url', models.URLField(blank=True, help_text='GitHub profile URL')),
                ('linkedin_url', models.URLField(blank=True, help_text='LinkedIn profile URL')),
                ('behance_url', models.URLField(blank=True, help_text='Behance/Dribbble URL')),
                ('availability_status', models.CharField(
                    choices=[
                        ('available', 'Available'),
                        ('busy', 'Busy'),
                        ('unavailable', 'Unavailable'),
                    ],
                    default='available',
                    max_length=20
                )),
                ('availability_notes', models.TextField(blank=True, help_text='Additional availability information')),
                ('timezone', models.CharField(default='UTC', max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('is_featured', models.BooleanField(default=False)),
                ('is_verified', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('skills', models.ManyToManyField(help_text='Skills and expertise tags', related_name='freelance_listings', to='accounts.skill')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='freelance_listing', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Freelance Listing',
                'verbose_name_plural': 'Freelance Listings',
                'ordering': ['-is_featured', '-created_at'],
            },
        ),
        
        # Create FreelancePortfolioItem model
        migrations.CreateModel(
            name='FreelancePortfolioItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_type', models.CharField(
                    choices=[
                        ('image', 'Image'),
                        ('link', 'Link'),
                        ('case_study', 'Case Study'),
                    ],
                    default='image',
                    max_length=20
                )),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='freelance/portfolio/')),
                ('url', models.URLField(blank=True, help_text='Portfolio link URL')),
                ('case_study_content', models.TextField(blank=True, help_text='Case study content (markdown supported)')),
                ('order', models.PositiveIntegerField(default=0)),
                ('is_featured', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('listing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='portfolio_items', to='accounts.freelancelisting')),
            ],
            options={
                'verbose_name': 'Portfolio Item',
                'verbose_name_plural': 'Portfolio Items',
                'ordering': ['-is_featured', 'order', '-created_at'],
            },
        ),
        
        # Create SkillSwapListing model
        migrations.CreateModel(
            name='SkillSwapListing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.TextField(help_text="Tell others about yourself and what you're looking for in skill swaps")),
                ('additional_skills_offered', models.CharField(blank=True, help_text='Comma-separated additional skills you offer', max_length=500)),
                ('additional_skills_wanted', models.CharField(blank=True, help_text='Comma-separated additional skills you want', max_length=500)),
                ('credits_earned', models.DecimalField(
                    decimal_places=2,
                    default=0,
                    help_text='Total credits earned (1 hour = 1 credit)',
                    max_digits=10,
                    validators=[django.core.validators.MinValueValidator(0)]
                )),
                ('credits_spent', models.DecimalField(
                    decimal_places=2,
                    default=0,
                    help_text='Total credits spent',
                    max_digits=10,
                    validators=[django.core.validators.MinValueValidator(0)]
                )),
                ('location_preference', models.CharField(blank=True, help_text='Preferred location for swaps (city, state or "remote")', max_length=100)),
                ('accepts_remote', models.BooleanField(default=True, help_text='Accept remote skill swaps')),
                ('is_active', models.BooleanField(default=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('skills_offered', models.ManyToManyField(help_text='Skills you can offer to others', related_name='swap_listings_offered', to='accounts.skill')),
                ('skills_wanted', models.ManyToManyField(help_text='Skills you want to learn or receive', related_name='swap_listings_wanted', to='accounts.skill')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='skill_swap_listing', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Skill Swap Listing',
                'verbose_name_plural': 'Skill Swap Listings',
                'ordering': ['-is_verified', '-created_at'],
            },
        ),
        
        # Create SkillCredit model
        migrations.CreateModel(
            name='SkillCredit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(
                    choices=[
                        ('earned', 'Earned'),
                        ('spent', 'Spent'),
                    ],
                    max_length=20
                )),
                ('credits', models.DecimalField(
                    decimal_places=2,
                    help_text='Number of credits (hours)',
                    max_digits=10,
                    validators=[django.core.validators.MinValueValidator(0)]
                )),
                ('description', models.TextField(help_text='Description of the skill swap')),
                ('swap_date', models.DateField(help_text='Date when the swap occurred')),
                ('status', models.CharField(
                    choices=[
                        ('pending', 'Pending'),
                        ('approved', 'Approved'),
                        ('rejected', 'Rejected'),
                    ],
                    default='pending',
                    max_length=20
                )),
                ('verified_at', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('from_user', models.ForeignKey(
                    help_text='User who provided the service',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='credits_given',
                    to=settings.AUTH_USER_MODEL
                )),
                ('skill_swapped', models.ForeignKey(
                    blank=True,
                    help_text='Skill that was swapped',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='accounts.skill'
                )),
                ('to_user', models.ForeignKey(
                    help_text='User who received the service',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='credits_received',
                    to=settings.AUTH_USER_MODEL
                )),
                ('verified_by', models.ForeignKey(
                    blank=True,
                    help_text='Admin or user who verified this transaction',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='credits_verified',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'Skill Credit',
                'verbose_name_plural': 'Skill Credits',
                'ordering': ['-swap_date', '-created_at'],
            },
        ),
    ]
