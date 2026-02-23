"""
Management command to generate comprehensive mock data for testing.
"""

import random
from decimal import Decimal
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from faker import Faker

from apps.providers.models import ServiceProvider, ServiceCategory
from apps.reviews.models import ProviderReview
from apps.accounts.models import CustomUser
from apps.accounts.modes_models import (
    Skill, SkillSwapListing, FreelanceListing, FreelancePortfolioItem,
    SkillSwapJob, SkillCredit
)
from apps.providers.unified_jobs import UnifiedJob, JobProposal
from apps.providers.community_projects import (
    CommunityProject, ProjectRole, ProjectApplication, ProjectMember
)
from apps.accounts.matching_models import Match
from apps.accounts.credit_service import CreditTransactionService

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = 'Generate comprehensive mock data for testing all features'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=50,
            help='Number of users to create (default: 50)',
        )
        parser.add_argument(
            '--jobs',
            type=int,
            default=30,
            help='Number of unified jobs to create (default: 30)',
        )
        parser.add_argument(
            '--projects',
            type=int,
            default=15,
            help='Number of community projects to create (default: 15)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before generating',
        )
        parser.add_argument(
            '--skip-superuser',
            action='store_true',
            help='Skip creating superuser',
        )
    
    def handle(self, *args, **options):
        users_count = options['users']
        jobs_count = options['jobs']
        projects_count = options['projects']
        clear_data = options['clear']
        skip_superuser = options['skip_superuser']
        
        self.stdout.write(self.style.SUCCESS('Starting mock data generation...'))
        
        if clear_data:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            self._clear_data()
        
        # Load categories and skills
        categories = list(ServiceCategory.objects.filter(is_active=True))
        skills = list(Skill.objects.filter(is_active=True))
        
        if not categories:
            self.stdout.write(self.style.ERROR('No categories found! Please load category fixtures first.'))
            return
        
        if not skills:
            self.stdout.write(self.style.ERROR('No skills found! Please load skill fixtures first.'))
            return
        
        # Cities for geographic distribution
        cities = [
            ('San Francisco', 'CA', '94102'),
            ('Oakland', 'CA', '94601'),
            ('Berkeley', 'CA', '94704'),
            ('San Jose', 'CA', '95110'),
            ('Los Angeles', 'CA', '90001'),
            ('San Diego', 'CA', '92101'),
            ('Seattle', 'WA', '98101'),
            ('Portland', 'OR', '97201'),
        ]
        
        with transaction.atomic():
            # Create superuser
            if not skip_superuser:
                self._create_superuser()
            
            # Generate users
            self.stdout.write(f'Generating {users_count} users...')
            users = self._generate_users(users_count, cities, categories, skills)
            
            # Generate skill swap listings
            self.stdout.write('Generating skill swap listings...')
            swap_listings = self._generate_skill_swaps(users, skills)
            
            # Generate freelance listings
            self.stdout.write('Generating freelance listings...')
            freelance_listings = self._generate_freelance(users, skills)
            
            # Generate provider profiles
            self.stdout.write('Generating provider profiles...')
            providers = self._generate_providers(users, categories)
            
            # Generate unified jobs
            self.stdout.write(f'Generating {jobs_count} unified jobs...')
            jobs = self._generate_unified_jobs(users, jobs_count, skills)
            
            # Generate credit transactions
            self.stdout.write('Generating credit transactions...')
            self._generate_credits(users, swap_listings)
            
            # Generate community projects
            self.stdout.write(f'Generating {projects_count} community projects...')
            self._generate_projects(users, projects_count, skills)
            
            # Generate reviews
            self.stdout.write('Generating reviews...')
            self._generate_reviews(users, providers)
            
            # Generate matches
            self.stdout.write('Generating matches...')
            self._generate_matches(users, skills)
        
        self.stdout.write(self.style.SUCCESS('\n✅ Mock data generation complete!'))
        self._print_summary(users, jobs_count, projects_count)
    
    def _create_superuser(self):
        """Create a test superuser."""
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@findapro.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                city='San Francisco',
                state='CA',
                zip_code='94102'
            )
            self.stdout.write(self.style.SUCCESS('Created superuser: admin/admin123'))
    
    def _generate_users(self, count, cities, categories, skills):
        """Generate users with diverse profile types."""
        users = []
        profile_types = ['pro', 'freelance', 'swap', 'hybrid', 'customer'] * (count // 5)
        profile_types += ['pro', 'freelance', 'swap'] * (count % 5)
        
        for i in range(count):
            city, state, zip_code = random.choice(cities)
            
            user = User.objects.create_user(
                username=fake.user_name() + str(i),
                email=fake.email(),
                password='password123',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                phone=fake.phone_number()[:20],
                bio=fake.text(max_nb_chars=200),
                city=city,
                state=state,
                zip_code=zip_code,
            )
            
            # Set profile type
            profile_type = profile_types[i] if i < len(profile_types) else 'customer'
            if profile_type == 'pro':
                user.user_type = 'provider'
            elif profile_type == 'freelance':
                user.is_freelancer_active = True
                user.active_mode = 'freelance'
            elif profile_type == 'swap':
                user.is_skill_swap_active = True
                user.active_mode = 'skill_swap'
            elif profile_type == 'hybrid':
                user.is_freelancer_active = True
                user.is_skill_swap_active = True
                user.active_mode = 'freelance'
            
            user.save()
            users.append(user)
            
            if (i + 1) % 10 == 0:
                self.stdout.write(f'  Created {i + 1}/{count} users...')
        
        return users
    
    def _generate_skill_swaps(self, users, skills):
        """Generate skill swap listings."""
        listings = []
        swap_users = [u for u in users if u.is_skill_swap_active or random.random() < 0.3]
        
        for user in swap_users[:50]:
            if not hasattr(user, 'skill_swap_listing'):
                listing = SkillSwapListing.objects.create(
                    user=user,
                    bio=fake.text(max_nb_chars=300),
                    credits_earned=Decimal(str(random.randint(0, 50))),
                    credits_spent=Decimal(str(random.randint(0, 30))),
                    accepts_remote=random.choice([True, False]),
                    location_preference=random.choice(['local', 'remote', 'both']),
                    is_active=True,
                    is_verified=random.choice([True, False]),
                )
                
                # Add skills
                offered_skills = random.sample(skills, random.randint(2, 5))
                wanted_skills = random.sample(skills, random.randint(1, 4))
                listing.skills_offered.set(offered_skills)
                listing.skills_wanted.set(wanted_skills)
                
                listings.append(listing)
        
        return listings
    
    def _generate_freelance(self, users, skills):
        """Generate freelance listings."""
        listings = []
        freelance_users = [u for u in users if u.is_freelancer_active or random.random() < 0.3]
        
        for user in freelance_users[:50]:
            if not hasattr(user, 'freelance_listing'):
                listing = FreelanceListing.objects.create(
                    user=user,
                    title=fake.job(),
                    bio=fake.text(max_nb_chars=400),
                    hourly_rate=Decimal(str(random.choice([25, 35, 50, 75, 100, 150, 200]))),
                    project_rate_min=Decimal(str(random.randint(500, 2000))),
                    project_rate_max=Decimal(str(random.randint(2000, 10000))),
                    currency='USD',
                    portfolio_url=fake.url() if random.random() < 0.7 else '',
                    availability_status=random.choice(['available', 'busy', 'unavailable']),
                    is_active=True,
                    is_featured=random.random() < 0.1,
                )
                
                # Add skills
                listing_skills = random.sample(skills, random.randint(3, 8))
                listing.skills.set(listing_skills)
                
                # Create portfolio items
                for _ in range(random.randint(1, 5)):
                    FreelancePortfolioItem.objects.create(
                        listing=listing,
                        item_type=random.choice(['image', 'link', 'case_study']),
                        title=fake.sentence(nb_words=3),
                        description=fake.text(max_nb_chars=200),
                        url=fake.url() if random.random() < 0.8 else '',
                        order=random.randint(0, 10),
                    )
                
                listings.append(listing)
        
        return listings
    
    def _generate_providers(self, users, categories):
        """Generate service provider profiles."""
        providers = []
        pro_users = [u for u in users if u.user_type == 'provider' or random.random() < 0.2]
        
        # Ensure we have enough provider users
        if len(pro_users) < 30:
            # Convert some regular users to providers
            regular_users = [u for u in users if u.user_type == 'customer']
            for user in regular_users[:30 - len(pro_users)]:
                user.user_type = 'provider'
                user.save()
                pro_users.append(user)
        
        # Create featured providers first (6-8 featured)
        featured_count = min(8, len(pro_users))
        for i, user in enumerate(pro_users[:featured_count]):
            if not hasattr(user, 'provider_profile'):
                category = random.choice(categories)
                provider = ServiceProvider.objects.create(
                    user=user,
                    name=fake.company(),
                    slug=fake.slug() + str(user.id),
                    description=fake.text(max_nb_chars=500),
                    tagline=fake.sentence(nb_words=6),
                    category=category,
                    skills=', '.join(fake.words(nb=5)),
                    email=user.email,
                    phone=user.phone,
                    website=fake.url() if random.random() < 0.7 else '',
                    address=fake.street_address(),
                    city=user.city,
                    state=user.state,
                    zip_code=user.zip_code,
                    pricing_range=random.choice(['$$', '$$$', '$$$$']),  # Featured providers tend to be mid-high range
                    years_experience=random.randint(5, 30),  # More experienced
                    is_verified=True,  # Featured providers are verified
                    is_active=True,
                    is_featured=True,  # Mark as featured
                    accepts_paid_jobs=True,
                    accepts_credit_jobs=random.random() < 0.5,
                    accepts_barter=random.random() < 0.3,
                )
                providers.append(provider)
        
        # Create regular providers
        for user in pro_users[featured_count:30]:
            if not hasattr(user, 'provider_profile'):
                category = random.choice(categories)
                provider = ServiceProvider.objects.create(
                    user=user,
                    name=fake.company(),
                    slug=fake.slug() + str(user.id),
                    description=fake.text(max_nb_chars=500),
                    tagline=fake.sentence(nb_words=6),
                    category=category,
                    skills=', '.join(fake.words(nb=5)),
                    email=user.email,
                    phone=user.phone,
                    website=fake.url() if random.random() < 0.6 else '',
                    address=fake.street_address(),
                    city=user.city,
                    state=user.state,
                    zip_code=user.zip_code,
                    pricing_range=random.choice(['$', '$$', '$$$', '$$$$']),
                    years_experience=random.randint(1, 30),
                    is_verified=random.random() < 0.3,
                    is_active=True,
                    is_featured=False,  # Regular providers not featured
                    accepts_paid_jobs=True,
                    accepts_credit_jobs=random.random() < 0.4,
                    accepts_barter=random.random() < 0.3,
                )
                providers.append(provider)
        
        return providers
    
    def _generate_unified_jobs(self, users, count, skills):
        """Generate unified jobs."""
        jobs = []
        payment_types = ['paid', 'credit', 'barter']
        
        for i in range(count):
            requester = random.choice(users)
            provider_user = random.choice([u for u in users if u != requester])
            
            # Get provider profile if exists
            provider = None
            if hasattr(provider_user, 'provider_profile'):
                provider = provider_user.provider_profile
            
            payment_type = random.choice(payment_types)
            status = random.choice(['pending', 'proposed', 'accepted', 'in_progress', 'completed'])
            
            job = UnifiedJob.objects.create(
                requester=requester,
                provider=provider_user if provider else None,
                payment_type=payment_type,
                title=fake.sentence(nb_words=4),
                description=fake.text(max_nb_chars=300),
                timeline=random.choice(['asap', 'this_week', 'next_week', 'this_month', 'flexible']),
                is_emergency=random.random() < 0.2,
                service_city=requester.city,
                service_state=requester.state,
                service_zip=requester.zip_code,
                status=status,
                requester_confirmed=status == 'completed',
                provider_confirmed=status == 'completed',
            )
            
            # Set payment-specific fields
            if payment_type == 'paid':
                job.budget_min = Decimal(str(random.randint(50, 500)))
                job.budget_max = Decimal(str(random.randint(500, 5000)))
                if status in ['accepted', 'completed']:
                    job.agreed_amount = Decimal(str(random.randint(100, 2000)))
            
            elif payment_type == 'credit':
                job.credits_requested = Decimal(str(random.choice([1, 2, 3, 4, 5, 8, 10])))
                if status in ['accepted', 'completed']:
                    job.credits_agreed = job.credits_requested
                    job.credits_in_escrow = job.credits_agreed if status == 'accepted' else 0
            
            elif payment_type == 'barter':
                job.barter_offer = fake.sentence(nb_words=8)
                job.barter_request = fake.sentence(nb_words=8)
            
            if status == 'completed':
                job.completed_at = timezone.now() - timedelta(days=random.randint(1, 30))
                job.payment_processed = True
            
            job.save()
            jobs.append(job)
        
        return jobs
    
    def _generate_credits(self, users, swap_listings):
        """Generate credit transaction history."""
        for listing in swap_listings[:30]:
            user = listing.user
            
            # Welcome bonus
            CreditTransactionService.award_bonus_credits(
                user=user,
                credits=Decimal('5'),
                description='Welcome bonus'
            )
            
            # Generate some earned credits
            for _ in range(random.randint(2, 8)):
                credit = SkillCredit.objects.create(
                    from_user=None,
                    to_user=user,
                    transaction_type='earned',
                    credits=Decimal(str(random.choice([1, 2, 3, 5]))),
                    description=fake.sentence(nb_words=6),
                    status='approved',
                    verified_at=timezone.now(),
                )
                CreditTransactionService.process_transaction(credit, auto_approve=True)
            
            # Generate some spent credits
            for _ in range(random.randint(1, 5)):
                credits = Decimal(str(random.choice([1, 2, 3])))
                balance = CreditTransactionService.get_user_balance(user)
                if balance >= credits:
                    to_user = random.choice([u for u in users if u != user])
                    credit = SkillCredit.objects.create(
                        from_user=user,
                        to_user=to_user,
                        transaction_type='spent',
                        credits=credits,
                        description=fake.sentence(nb_words=6),
                        status='approved',
                        verified_at=timezone.now(),
                    )
                    CreditTransactionService.process_transaction(credit, auto_approve=True)
    
    def _generate_projects(self, users, count, skills):
        """Generate community projects."""
        project_types = ['community', 'creative', 'business', 'learning']
        compensation_types = ['paid', 'credits', 'volunteer', 'mixed']
        
        for i in range(count):
            creator = random.choice(users)
            project_type = random.choice(project_types)
            compensation_type = random.choice(compensation_types)
            
            project = CommunityProject.objects.create(
                creator=creator,
                title=fake.sentence(nb_words=5),
                description=fake.text(max_nb_chars=500),
                project_type=project_type,
                status=random.choice(['recruiting', 'in_progress', 'completed']),
                start_date=timezone.now().date() + timedelta(days=random.randint(-30, 30)),
                end_date=timezone.now().date() + timedelta(days=random.randint(30, 180)),
                timeline_description=random.choice(['3 months', '6 months', 'Ongoing', '1 year']),
                location_city=creator.city,
                location_state=creator.state,
                location_address=fake.street_address(),
                location_zip=creator.zip_code,
                is_remote_friendly=random.choice([True, False]),
                compensation_type=compensation_type,
                budget_total=Decimal(str(random.randint(1000, 50000))) if compensation_type in ['paid', 'mixed'] else None,
                is_featured=random.random() < 0.2,
                published_at=timezone.now() - timedelta(days=random.randint(1, 60)),
            )
            
            # Create project member for creator
            ProjectMember.objects.create(
                project=project,
                user=creator,
                is_creator=True,
                is_lead=True,
                role_title='Project Creator',
            )
            
            # Create roles
            num_roles = random.randint(2, 5)
            for j in range(num_roles):
                role_skill = random.choice(skills)
                role_status = 'filled' if j < num_roles // 2 else 'open'
                role_compensation_type = random.choice(['paid', 'credits', 'volunteer'])
                
                role = ProjectRole.objects.create(
                    project=project,
                    title=fake.job(),
                    description=fake.text(max_nb_chars=200),
                    skill_required=role_skill,
                    time_commitment_hours=Decimal(str(random.choice([5, 10, 15, 20]))),
                    time_commitment_description=f"{random.choice([5, 10, 15, 20])} hours/week",
                    experience_level=random.choice(['beginner', 'intermediate', 'advanced', 'expert']),
                    compensation_type=role_compensation_type,
                    compensation_amount=Decimal(str(random.randint(20, 100))) if role_compensation_type == 'paid' else None,
                    compensation_description=fake.sentence(nb_words=4),
                    status=role_status,
                )
                
                # Fill some roles
                if role_status == 'filled':
                    team_member = random.choice([u for u in users if u != creator])
                    role.filled_by = team_member
                    role.filled_at = timezone.now() - timedelta(days=random.randint(1, 30))
                    role.save()
                    
                    ProjectMember.objects.create(
                        project=project,
                        user=team_member,
                        role=role,
                        role_title=role.title,
                    )
                
                # Create applications for open roles
                if role_status == 'open':
                    for _ in range(random.randint(1, 4)):
                        applicant = random.choice([u for u in users if u != creator])
                        if not ProjectApplication.objects.filter(role=role, applicant=applicant).exists():
                            ProjectApplication.objects.create(
                                role=role,
                                applicant=applicant,
                                cover_letter=fake.text(max_nb_chars=300),
                                relevant_experience=fake.text(max_nb_chars=200),
                                status=random.choice(['pending', 'accepted', 'declined']),
                            )
    
    def _generate_reviews(self, users, providers):
        """Generate reviews for providers."""
        # Generate more reviews for featured providers to ensure they have good ratings
        featured_providers = [p for p in providers if p.is_featured]
        regular_providers = [p for p in providers if not p.is_featured]
        
        # Featured providers get more reviews with higher ratings
        for provider in featured_providers:
            available_reviewers = [u for u in users if u != provider.user]
            num_reviews = min(random.randint(5, 12), len(available_reviewers))
            reviewers_used = set()
            
            for _ in range(num_reviews):
                potential_reviewers = [u for u in available_reviewers if u not in reviewers_used]
                if not potential_reviewers:
                    break
                
                reviewer = random.choice(potential_reviewers)
                reviewers_used.add(reviewer)
                
                if not ProviderReview.objects.filter(user=reviewer, provider=provider).exists():
                    # Featured providers get mostly 4-5 star reviews
                    ProviderReview.objects.create(
                        user=reviewer,
                        provider=provider,
                        rating=random.choice([4, 4, 4, 5, 5, 5, 5]),
                        title=fake.sentence(nb_words=4),
                        comment=fake.text(max_nb_chars=300),
                        would_recommend=True,  # Featured providers always recommended
                        service_date=timezone.now().date() - timedelta(days=random.randint(1, 180)),
                    )
        
        # Regular providers get fewer reviews
        for provider in regular_providers[:20]:
            available_reviewers = [u for u in users if u != provider.user]
            num_reviews = min(random.randint(2, 8), len(available_reviewers))
            reviewers_used = set()
            
            for _ in range(num_reviews):
                potential_reviewers = [u for u in available_reviewers if u not in reviewers_used]
                if not potential_reviewers:
                    break
                
                reviewer = random.choice(potential_reviewers)
                reviewers_used.add(reviewer)
                
                if not ProviderReview.objects.filter(user=reviewer, provider=provider).exists():
                    ProviderReview.objects.create(
                        user=reviewer,
                        provider=provider,
                        rating=random.choice([3, 4, 4, 4, 5, 5, 5]),
                        title=fake.sentence(nb_words=4),
                        comment=fake.text(max_nb_chars=300),
                        would_recommend=random.random() < 0.8,
                        service_date=timezone.now().date() - timedelta(days=random.randint(1, 180)),
                    )
    
    def _generate_matches(self, users, skills):
        """Generate some high-compatibility matches."""
        swap_users = [u for u in users if hasattr(u, 'skill_swap_listing') and u.skill_swap_listing.is_active]
        
        for _ in range(min(20, len(swap_users) // 2)):
            user_a = random.choice(swap_users)
            user_b = random.choice([u for u in swap_users if u != user_a])
            
            if not Match.objects.filter(
                (Q(user_a=user_a, user_b=user_b) | Q(user_a=user_b, user_b=user_a))
            ).exists():
                # Calculate compatibility
                if hasattr(user_a, 'skill_swap_listing') and hasattr(user_b, 'skill_swap_listing'):
                    a_offered = set(user_a.skill_swap_listing.skills_offered.all())
                    b_wanted = set(user_b.skill_swap_listing.skills_wanted.all())
                    overlap = len(a_offered & b_wanted)
                    
                    if overlap > 0:
                        matching_skills_list = [skill.name for skill in list(a_offered & b_wanted)[:5]]
                        overlap_pct = (overlap / max(len(a_offered), len(b_wanted))) * 100 if max(len(a_offered), len(b_wanted)) > 0 else 0
                        Match.objects.create(
                            user_a=user_a,
                            user_b=user_b,
                            match_type='skill_swap',
                            compatibility_score=Decimal(str(min(95, 60 + (overlap * 10)))),
                            matching_skills=matching_skills_list,
                            skill_overlap_percentage=Decimal(str(min(100, overlap_pct))),
                            status=random.choice(['pending', 'viewed', 'interested']),
                        )
    
    def _clear_data(self):
        """Clear existing data (except superuser and categories/skills)."""
        ProjectApplication.objects.all().delete()
        ProjectMember.objects.all().delete()
        ProjectRole.objects.all().delete()
        CommunityProject.objects.all().delete()
        UnifiedJob.objects.all().delete()
        JobProposal.objects.all().delete()
        ProviderReview.objects.all().delete()
        ServiceProvider.objects.all().delete()
        SkillSwapJob.objects.all().delete()
        SkillCredit.objects.all().delete()
        FreelancePortfolioItem.objects.all().delete()
        FreelanceListing.objects.all().delete()
        SkillSwapListing.objects.all().delete()
        Match.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()
    
    def _print_summary(self, users, jobs_count, projects_count):
        """Print summary of created data."""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('📊 DATA GENERATION SUMMARY'))
        self.stdout.write('='*60)
        self.stdout.write(f'Users: {len(users)}')
        self.stdout.write(f'  - Provider profiles: {ServiceProvider.objects.count()}')
        self.stdout.write(f'  - Skill swap listings: {SkillSwapListing.objects.count()}')
        self.stdout.write(f'  - Freelance listings: {FreelanceListing.objects.count()}')
        self.stdout.write(f'Unified Jobs: {UnifiedJob.objects.count()}')
        self.stdout.write(f'Community Projects: {CommunityProject.objects.count()}')
        self.stdout.write(f'  - Open roles: {ProjectRole.objects.filter(status="open").count()}')
        self.stdout.write(f'  - Applications: {ProjectApplication.objects.count()}')
        self.stdout.write(f'Credit Transactions: {SkillCredit.objects.count()}')
        self.stdout.write(f'Reviews: {ProviderReview.objects.count()}')
        self.stdout.write(f'Matches: {Match.objects.count()}')
        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS('\n✅ Test with: admin/admin123'))
