"""
Management command to populate the database with mock data.
"""

import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.providers.models import ServiceCategory, ServiceProvider
from apps.reviews.models import ProviderReview

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate database with mock data'

    def handle(self, *args, **options):
        self.stdout.write('Creating mock data...\n')
        
        # Create categories
        categories = self.create_categories()
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(categories)} categories'))
        
        # Create users
        users = self.create_users()
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(users)} users'))
        
        # Create providers
        providers = self.create_providers(categories)
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(providers)} providers'))
        
        # Create reviews
        reviews = self.create_reviews(users, providers)
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(reviews)} reviews'))
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Mock data populated successfully!'))
        self.stdout.write(self.style.WARNING('\n📸 To add gallery images, use the Django Admin panel.'))

    def create_categories(self):
        categories_data = [
            {
                'name': 'Plumbing',
                'slug': 'plumbing',
                'description': 'Professional plumbing services including repairs, installations, and emergency services.',
                'icon': '🔧'
            },
            {
                'name': 'Electrical',
                'slug': 'electrical',
                'description': 'Licensed electricians for residential and commercial electrical work.',
                'icon': '⚡'
            },
            {
                'name': 'Cleaning',
                'slug': 'cleaning',
                'description': 'Home and office cleaning services, deep cleaning, and move-in/move-out cleaning.',
                'icon': '🧹'
            },
            {
                'name': 'HVAC',
                'slug': 'hvac',
                'description': 'Heating, ventilation, and air conditioning installation and repair.',
                'icon': '❄️'
            },
            {
                'name': 'Landscaping',
                'slug': 'landscaping',
                'description': 'Lawn care, garden design, tree services, and outdoor maintenance.',
                'icon': '🌳'
            },
            {
                'name': 'Painting',
                'slug': 'painting',
                'description': 'Interior and exterior painting services for homes and businesses.',
                'icon': '🎨'
            },
            {
                'name': 'Roofing',
                'slug': 'roofing',
                'description': 'Roof repair, replacement, and installation services.',
                'icon': '🏠'
            },
            {
                'name': 'Moving',
                'slug': 'moving',
                'description': 'Local and long-distance moving services, packing, and storage.',
                'icon': '📦'
            },
            {
                'name': 'Handyman',
                'slug': 'handyman',
                'description': 'General repairs, installations, and home improvement services.',
                'icon': '🔨'
            },
            {
                'name': 'Auto Repair',
                'slug': 'auto-repair',
                'description': 'Automotive repair, maintenance, and detailing services.',
                'icon': '🚗'
            },
        ]
        
        categories = []
        for data in categories_data:
            cat, created = ServiceCategory.objects.get_or_create(
                slug=data['slug'],
                defaults=data
            )
            categories.append(cat)
        
        return categories

    def create_users(self):
        users_data = [
            {'username': 'john_doe', 'email': 'john@example.com', 'first_name': 'John', 'last_name': 'Doe', 'city': 'San Francisco', 'state': 'CA'},
            {'username': 'jane_smith', 'email': 'jane@example.com', 'first_name': 'Jane', 'last_name': 'Smith', 'city': 'Los Angeles', 'state': 'CA'},
            {'username': 'mike_johnson', 'email': 'mike@example.com', 'first_name': 'Mike', 'last_name': 'Johnson', 'city': 'Seattle', 'state': 'WA'},
            {'username': 'sarah_wilson', 'email': 'sarah@example.com', 'first_name': 'Sarah', 'last_name': 'Wilson', 'city': 'Portland', 'state': 'OR'},
            {'username': 'david_brown', 'email': 'david@example.com', 'first_name': 'David', 'last_name': 'Brown', 'city': 'Denver', 'state': 'CO'},
            {'username': 'emily_davis', 'email': 'emily@example.com', 'first_name': 'Emily', 'last_name': 'Davis', 'city': 'Austin', 'state': 'TX'},
            {'username': 'chris_miller', 'email': 'chris@example.com', 'first_name': 'Chris', 'last_name': 'Miller', 'city': 'Chicago', 'state': 'IL'},
            {'username': 'lisa_garcia', 'email': 'lisa@example.com', 'first_name': 'Lisa', 'last_name': 'Garcia', 'city': 'Phoenix', 'state': 'AZ'},
            {'username': 'tom_martinez', 'email': 'tom@example.com', 'first_name': 'Tom', 'last_name': 'Martinez', 'city': 'San Diego', 'state': 'CA'},
            {'username': 'amy_anderson', 'email': 'amy@example.com', 'first_name': 'Amy', 'last_name': 'Anderson', 'city': 'Miami', 'state': 'FL'},
        ]
        
        users = []
        for data in users_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    **data,
                    'user_type': 'customer'
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            users.append(user)
        
        return users

    def create_providers(self, categories):
        providers_data = [
            # Plumbing
            {
                'name': 'Quick Fix Plumbing',
                'slug': 'quick-fix-plumbing',
                'tagline': 'Fast, reliable plumbing solutions',
                'description': 'With over 15 years of experience, Quick Fix Plumbing provides top-notch residential and commercial plumbing services. From leaky faucets to complete pipe replacements, we handle it all with professionalism and care.',
                'category_slug': 'plumbing',
                'skills': 'leak repair, pipe fitting, drain cleaning, water heater installation, bathroom remodeling',
                'email': 'info@quickfixplumbing.com',
                'phone': '(555) 123-4567',
                'city': 'San Francisco',
                'state': 'CA',
                'zip_code': '94102',
                'pricing_range': '$$',
                'years_experience': 15,
                'is_verified': True,
                'is_featured': True,
                'accepts_emergency': True,
                'is_available_now': True,
                'emergency_rate_info': '25% premium for after-hours',
            },
            {
                'name': 'Bay Area Plumbers',
                'slug': 'bay-area-plumbers',
                'tagline': '24/7 Emergency plumbing services',
                'description': 'Bay Area Plumbers offers round-the-clock emergency services. Our licensed team handles everything from minor repairs to major installations with guaranteed satisfaction.',
                'category_slug': 'plumbing',
                'skills': 'emergency repairs, sewer line repair, gas line installation, fixture installation',
                'email': 'contact@bayareaplumbers.com',
                'phone': '(555) 234-5678',
                'city': 'Oakland',
                'state': 'CA',
                'zip_code': '94612',
                'pricing_range': '$$$',
                'years_experience': 20,
                'is_verified': True,
                'is_featured': False,
                'accepts_emergency': True,
                'is_available_now': False,
                'emergency_rate_info': 'Emergency service available 24/7',
            },
            # Electrical
            {
                'name': 'Bright Spark Electric',
                'slug': 'bright-spark-electric',
                'tagline': 'Powering your home safely',
                'description': 'Bright Spark Electric is your trusted partner for all electrical needs. We specialize in residential electrical work, smart home installations, and energy-efficient upgrades.',
                'category_slug': 'electrical',
                'skills': 'wiring, panel upgrades, lighting installation, smart home setup, electrical inspections',
                'email': 'hello@brightspark.com',
                'phone': '(555) 345-6789',
                'city': 'Los Angeles',
                'state': 'CA',
                'zip_code': '90001',
                'pricing_range': '$$',
                'years_experience': 12,
                'is_verified': True,
                'is_featured': True,
                'accepts_emergency': True,
                'is_available_now': True,
                'emergency_rate_info': 'Same-day service available',
            },
            {
                'name': 'PowerPro Electrical',
                'slug': 'powerpro-electrical',
                'tagline': 'Commercial & residential experts',
                'description': 'PowerPro Electrical serves both commercial and residential clients with expert electrical services. Fully licensed and insured for your peace of mind.',
                'category_slug': 'electrical',
                'skills': 'commercial wiring, EV charger installation, generator installation, troubleshooting',
                'email': 'service@powerpro.com',
                'phone': '(555) 456-7890',
                'city': 'San Jose',
                'state': 'CA',
                'zip_code': '95101',
                'pricing_range': '$$$',
                'years_experience': 18,
                'is_verified': True,
                'is_featured': False,
            },
            # Cleaning
            {
                'name': 'Sparkle Clean Co',
                'slug': 'sparkle-clean-co',
                'tagline': 'Making your space shine',
                'description': 'Sparkle Clean Co provides eco-friendly cleaning services for homes and offices. Our trained professionals use green products to deliver spotless results.',
                'category_slug': 'cleaning',
                'skills': 'deep cleaning, move-in/move-out cleaning, office cleaning, carpet cleaning',
                'email': 'book@sparkleclean.com',
                'phone': '(555) 567-8901',
                'city': 'Seattle',
                'state': 'WA',
                'zip_code': '98101',
                'pricing_range': '$',
                'years_experience': 8,
                'is_verified': True,
                'is_featured': True,
            },
            {
                'name': 'Fresh & Tidy',
                'slug': 'fresh-and-tidy',
                'tagline': 'Your home, refreshed',
                'description': 'Fresh & Tidy offers flexible cleaning schedules to fit your busy life. Weekly, bi-weekly, or one-time cleaning services available.',
                'category_slug': 'cleaning',
                'skills': 'regular house cleaning, spring cleaning, post-construction cleaning, sanitization',
                'email': 'info@freshandtidy.com',
                'phone': '(555) 678-9012',
                'city': 'Portland',
                'state': 'OR',
                'zip_code': '97201',
                'pricing_range': '$$',
                'years_experience': 5,
                'is_verified': False,
                'is_featured': False,
            },
            # HVAC
            {
                'name': 'Cool Comfort HVAC',
                'slug': 'cool-comfort-hvac',
                'tagline': 'Stay comfortable year-round',
                'description': 'Cool Comfort HVAC provides installation, repair, and maintenance for all heating and cooling systems. Energy-efficient solutions for every budget.',
                'category_slug': 'hvac',
                'skills': 'AC installation, furnace repair, duct cleaning, thermostat installation, maintenance plans',
                'email': 'service@coolcomfort.com',
                'phone': '(555) 789-0123',
                'city': 'Phoenix',
                'state': 'AZ',
                'zip_code': '85001',
                'pricing_range': '$$$',
                'years_experience': 22,
                'is_verified': True,
                'is_featured': True,
                'accepts_emergency': True,
                'is_available_now': True,
                'emergency_rate_info': '24/7 emergency HVAC service',
            },
            # Landscaping
            {
                'name': 'Green Thumb Gardens',
                'slug': 'green-thumb-gardens',
                'tagline': 'Transform your outdoor space',
                'description': 'Green Thumb Gardens creates beautiful outdoor living spaces. From lawn maintenance to complete landscape design, we bring your vision to life.',
                'category_slug': 'landscaping',
                'skills': 'lawn care, garden design, irrigation systems, tree trimming, hardscaping',
                'email': 'hello@greenthumb.com',
                'phone': '(555) 890-1234',
                'city': 'Denver',
                'state': 'CO',
                'zip_code': '80201',
                'pricing_range': '$$',
                'years_experience': 10,
                'is_verified': True,
                'is_featured': False,
            },
            # Painting
            {
                'name': 'Perfect Coat Painters',
                'slug': 'perfect-coat-painters',
                'tagline': 'Flawless finishes every time',
                'description': 'Perfect Coat Painters delivers premium painting services with attention to detail. Interior, exterior, and specialty finishes available.',
                'category_slug': 'painting',
                'skills': 'interior painting, exterior painting, cabinet refinishing, wallpaper removal, color consultation',
                'email': 'quote@perfectcoat.com',
                'phone': '(555) 901-2345',
                'city': 'Austin',
                'state': 'TX',
                'zip_code': '78701',
                'pricing_range': '$$',
                'years_experience': 14,
                'is_verified': True,
                'is_featured': True,
            },
            # Roofing
            {
                'name': 'Top Notch Roofing',
                'slug': 'top-notch-roofing',
                'tagline': 'Protecting what matters most',
                'description': 'Top Notch Roofing specializes in residential and commercial roofing. New installations, repairs, and inspections with warranty-backed work.',
                'category_slug': 'roofing',
                'skills': 'shingle roofing, flat roofing, roof repair, gutter installation, roof inspections',
                'email': 'info@topnotchroofing.com',
                'phone': '(555) 012-3456',
                'city': 'Chicago',
                'state': 'IL',
                'zip_code': '60601',
                'pricing_range': '$$$',
                'years_experience': 25,
                'is_verified': True,
                'is_featured': False,
                'accepts_emergency': True,
                'is_available_now': False,
                'emergency_rate_info': 'Storm damage repairs available',
            },
            # Moving
            {
                'name': 'Swift Movers',
                'slug': 'swift-movers',
                'tagline': 'Moving made easy',
                'description': 'Swift Movers provides stress-free moving services. Local and long-distance moves, packing services, and secure storage options available.',
                'category_slug': 'moving',
                'skills': 'local moving, long-distance moving, packing services, furniture assembly, storage',
                'email': 'move@swiftmovers.com',
                'phone': '(555) 111-2222',
                'city': 'San Diego',
                'state': 'CA',
                'zip_code': '92101',
                'pricing_range': '$$',
                'years_experience': 9,
                'is_verified': True,
                'is_featured': True,
            },
            # Handyman
            {
                'name': 'Handy Helper Services',
                'slug': 'handy-helper-services',
                'tagline': 'No job too small',
                'description': 'Handy Helper Services tackles all those odd jobs around your home. From mounting TVs to fixing squeaky doors, we do it all.',
                'category_slug': 'handyman',
                'skills': 'furniture assembly, drywall repair, door installation, fixture mounting, minor repairs',
                'email': 'help@handyhelper.com',
                'phone': '(555) 222-3333',
                'city': 'Miami',
                'state': 'FL',
                'zip_code': '33101',
                'pricing_range': '$',
                'years_experience': 7,
                'is_verified': True,
                'is_featured': False,
            },
            # Auto Repair
            {
                'name': 'Precision Auto Care',
                'slug': 'precision-auto-care',
                'tagline': 'Your car deserves the best',
                'description': 'Precision Auto Care offers comprehensive automotive services. From oil changes to major repairs, our ASE-certified mechanics deliver quality work.',
                'category_slug': 'auto-repair',
                'skills': 'oil change, brake repair, engine diagnostics, transmission repair, tire services',
                'email': 'service@precisionauto.com',
                'phone': '(555) 333-4444',
                'city': 'Las Vegas',
                'state': 'NV',
                'zip_code': '89101',
                'pricing_range': '$$',
                'years_experience': 16,
                'is_verified': True,
                'is_featured': True,
            },
        ]
        
        providers = []
        for data in providers_data:
            category = ServiceCategory.objects.get(slug=data.pop('category_slug'))
            provider, created = ServiceProvider.objects.get_or_create(
                slug=data['slug'],
                defaults={
                    **data,
                    'category': category,
                    'is_active': True,
                }
            )
            providers.append(provider)
        
        return providers

    def create_reviews(self, users, providers):
        review_templates = [
            {'rating': 5, 'title': 'Exceptional service!', 'comment': 'Absolutely fantastic experience. They arrived on time, were professional, and did an amazing job. Would definitely recommend to anyone looking for quality work.', 'would_recommend': True},
            {'rating': 5, 'title': 'Highly recommend', 'comment': 'Best service I\'ve ever received. The team was knowledgeable, efficient, and left everything spotless. Will definitely use again!', 'would_recommend': True},
            {'rating': 4, 'title': 'Great work', 'comment': 'Very pleased with the work done. Professional team, fair pricing, and good communication throughout the project.', 'would_recommend': True},
            {'rating': 4, 'title': 'Solid service', 'comment': 'Good experience overall. The work was completed as expected and the pricing was reasonable. Minor scheduling hiccup but resolved quickly.', 'would_recommend': True},
            {'rating': 5, 'title': 'Above and beyond', 'comment': 'They went above and beyond my expectations. Noticed a potential issue and fixed it before it became a bigger problem. Truly caring professionals.', 'would_recommend': True},
            {'rating': 3, 'title': 'Decent but room for improvement', 'comment': 'The work itself was fine, but communication could have been better. Had to follow up multiple times for updates.', 'would_recommend': True},
            {'rating': 5, 'title': 'Fast and reliable', 'comment': 'Called in the morning and they were here by afternoon. Fixed everything quickly and efficiently. Great emergency service!', 'would_recommend': True},
            {'rating': 4, 'title': 'Professional team', 'comment': 'Very professional from start to finish. They explained everything clearly and provided a detailed quote upfront. No surprises.', 'would_recommend': True},
            {'rating': 5, 'title': 'Couldn\'t be happier', 'comment': 'From the initial consultation to the final walkthrough, everything was perfect. The attention to detail was impressive.', 'would_recommend': True},
            {'rating': 4, 'title': 'Good value', 'comment': 'Fair prices for quality work. They were upfront about costs and didn\'t try to upsell unnecessary services.', 'would_recommend': True},
        ]
        
        reviews = []
        for provider in providers:
            # Each provider gets 3-6 random reviews
            num_reviews = random.randint(3, 6)
            reviewer_users = random.sample(users, min(num_reviews, len(users)))
            
            for user in reviewer_users:
                template = random.choice(review_templates)
                review, created = ProviderReview.objects.get_or_create(
                    user=user,
                    provider=provider,
                    defaults={
                        'rating': template['rating'],
                        'title': template['title'],
                        'comment': template['comment'],
                        'would_recommend': template['would_recommend'],
                        'helpful_count': random.randint(0, 15),
                    }
                )
                if created:
                    reviews.append(review)
        
        return reviews

