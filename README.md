# FindAPro - Local Services Marketplace

A modern Angie's List-style platform built with Django 5, Django REST Framework, TailwindCSS, Node.js, PostgreSQL, and Docker. Connect with local professionals for plumbing, electrical, cleaning, mechanics, and more.

<div align="center">
  <img src="docs/images/homepage.png" alt="FindAPro Homepage" width="900"/>
</div>

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-5.0-green)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-cyan)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)

## Features

### Core Features
- **Search & Filter** - Find professionals by skill, category, location (city/zip)
- **Reviews & Ratings** - Real customer reviews with 5-star ratings
- **Verified Providers** - Verified badge system for trusted professionals
- **User Dashboard** - Manage your profile and reviews
- **Responsive Design** - Beautiful UI with TailwindCSS
- **Authentication** - Complete login/register system
- **REST API** - Full API for providers, categories, and reviews

### Advanced Features
- **Smart Matching Quiz** - Interactive 5-step questionnaire to find your perfect provider match
- **Emergency Mode** - Find available providers for urgent jobs with real-time availability
- **Side-by-Side Compare** - Compare up to 3 providers at once (rating, pricing, experience, skills)
- **Favorites System** - Save providers to your favorites list for quick access
- **Quote Request System** - Request quotes from providers, track responses, and manage requests
- **Provider Gallery/Portfolio** - View provider work samples with lightbox image viewer
- **Provider Profile Creation** - Multi-step profile builder for professionals to join and create business profiles
- **Business Hours Management** - Set weekly business hours for each day of the week
- **Service Areas** - Define coverage zones with ZIP codes and radius
- **Certifications & Licenses** - Optional certification tracking with verification documents
- **Profile Completeness Tracking** - Real-time completion percentage with 50% minimum to go live

## Tech Stack

- **Backend**: Django 5 + Django REST Framework
- **Frontend**: Django Templates + TailwindCSS
- **Database**: PostgreSQL 16
- **Containerization**: Docker + Docker Compose
- **CSS Framework**: TailwindCSS 3.4

## Quick Start with Docker

### Prerequisites

- Docker and Docker Compose installed
- Git

### 1. Clone and Configure

```bash
cd FindAPro

# Create environment file
cp env.sample .env

# Edit .env with your settings (or use defaults for development)
```

### 2. Build and Run

```bash
# Build and start all containers
docker-compose up --build

# This will:
# - Start PostgreSQL database
# - Run Django migrations
# - Build TailwindCSS
# - Collect static files
# - Create a default superuser (admin/adminpassword)
# - Start the development server
```

### 3. Access the Application

- **Web App**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **API Root**: http://localhost:8000/api/

Default superuser credentials:
- Username: `admin`
- Password: `adminpassword`

## Development Setup (Without Docker)

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL 16

### 1. Setup Python Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup Node.js & TailwindCSS

```bash
# Install Node dependencies
npm install

# Build TailwindCSS (one-time)
npm run build:css

# Or watch for changes during development
npm run watch:css
```

### 3. Configure Environment

```bash
# Create .env file
cp env.sample .env

# Edit .env with your database settings
# For local development, update POSTGRES_HOST to 'localhost'
```

### 4. Setup Database

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic
```

### 5. Run Development Server

```bash
python manage.py runserver
```

## Docker Commands

```bash
# Start containers
docker-compose up

# Start in background
docker-compose up -d

# Stop containers
docker-compose down

# View logs
docker-compose logs -f web

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic

# Open Django shell
docker-compose exec web python manage.py shell

# Run management commands
docker-compose exec web python manage.py <command>

# Rebuild containers
docker-compose up --build
```

## TailwindCSS Commands

```bash
# Build CSS (production)
npm run build:css

# Watch for changes (development)
npm run watch:css
```

When using Docker, the Tailwind watcher runs in a separate container automatically.

## Main URL Routes

### Public Routes
- `/` - Homepage with search
- `/providers/` - Provider search and listing
- `/providers/match/` - Smart Matching Quiz
- `/providers/emergency/` - Emergency Mode
- `/providers/compare/` - Compare Providers
- `/providers/categories/` - Browse categories
- `/providers/<slug>/` - Provider detail page
- `/accounts/login/` - Login
- `/accounts/register/` - Register

### Authenticated Routes
- `/accounts/dashboard/` - User dashboard
- `/providers/favorites/` - My favorites
- `/providers/quotes/` - My quote requests
- `/providers/quotes/received/` - Provider's received quotes
- `/providers/<slug>/request-quote/` - Request a quote

### Provider Profile Routes
- `/providers/join/` - Join as a professional (landing page)
- `/providers/profile/create/` - Multi-step profile creation wizard
- `/providers/profile/preview/` - Preview profile before submission
- `/providers/profile/status/` - View profile status and completion
- `/providers/profile/edit/` - Edit existing provider profile

### Admin
- `/admin/` - Django admin panel

## Project Structure

```
FindAPro/
├── apps/
│   ├── accounts/      # Custom user model, authentication
│   ├── providers/     # Service providers, categories, search
│   ├── reviews/       # User reviews on providers
│   └── core/          # Homepage, utilities, base views
├── config/            # Django project settings
├── templates/         # HTML templates
│   ├── base.html
│   ├── accounts/
│   ├── providers/
│   ├── reviews/
│   └── core/
├── static/
│   ├── src/           # TailwindCSS input
│   └── css/           # TailwindCSS output
├── scripts/           # Docker entrypoint scripts
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── package.json
└── tailwind.config.js
```

## Key Features Explained

### 🎯 Smart Matching Quiz
Take an interactive 5-step quiz to find providers that match your needs:
1. Select service category
2. Enter your location
3. Choose urgency level
4. Select budget range
5. Pick your priority (quality, speed, price, or reviews)

The algorithm scores providers based on your preferences and shows top matches with match percentages and reasons.

**URL**: `/providers/match/`

### 🚨 Emergency Mode
Find providers available for urgent jobs right now:
- Filters to only emergency-ready providers
- Shows "Available NOW" vs "Accepts Emergencies"
- Direct call buttons for immediate contact
- Emergency rate information displayed

**URL**: `/providers/emergency/`

### ⚖️ Side-by-Side Compare
Compare up to 3 providers simultaneously:
- Rating, reviews, pricing comparison
- Experience, location, verification status
- Skills and services offered
- Emergency availability
- Quick action buttons (View Profile, Request Quote, Call)

**URL**: `/providers/compare/?ids=1,2,3`

### ❤️ Favorites System
Save providers to your favorites:
- One-click save/unsave
- Dedicated favorites page
- Accessible from navigation

**URL**: `/providers/favorites/`

### 📋 Quote Request System
Request and manage quotes:
- Customers can request quotes from providers
- Providers can respond with pricing
- Track quote status (pending, quoted, accepted, declined)
- Support for emergency requests

**URLs**: 
- Request: `/providers/<slug>/request-quote/`
- My Quotes: `/providers/quotes/`
- Provider Quotes: `/providers/quotes/received/`

### 🖼️ Provider Gallery
View provider portfolios:
- Multiple images per provider
- Featured image support
- Lightbox viewer for full-size images
- Captions and alt text for accessibility

**Access**: View on provider detail pages

### 👔 Provider Profile Creation
Comprehensive multi-step profile builder for professionals:

**5-Step Creation Process:**
1. **Basic Information** - Business name, category, tagline, description, skills
2. **Contact & Location** - Email, phone, website, full address
3. **Business Details** - Pricing range, years of experience, business hours, service areas
4. **Media & Portfolio** - Logo upload, main image, gallery images
5. **Availability & Emergency** - Availability status, emergency acceptance, rate information

**Key Features:**
- **Draft Mode** - Save progress and complete later
- **Progress Tracking** - Real-time completion percentage with visual progress bar
- **50% Minimum** - Must complete at least 50% of profile to submit
- **Immediate Activation** - Profiles go live immediately upon submission (no approval needed)
- **Business Hours** - Set weekly schedule for each day (open/close times or closed)
- **Service Areas** - Add multiple service locations with ZIP codes and radius
- **Certifications** - Optional certification tracking (admin verification available)

**Registration Flow:**
- New users can select "Service Provider" during registration → automatically redirected to profile creation
- Existing users can click "Join as Pro" from navigation or homepage
- One profile per user (enforced)

**URLs**: 
- Join: `/providers/join/`
- Create: `/providers/profile/create/`
- Status: `/providers/profile/status/`
- Edit: `/providers/profile/edit/`

## API Endpoints

### Providers

```
GET    /api/providers/           # List all providers
GET    /api/providers/?category= # Filter by category
GET    /api/providers/?city=     # Filter by city
GET    /api/providers/?zip=      # Filter by zip code
GET    /api/providers/?verified= # Filter verified only
GET    /api/providers/<id>/      # Provider detail
GET    /api/providers/featured/  # Featured providers
GET    /api/providers/top_rated/ # Top rated providers
```

### Categories

```
GET    /api/categories/          # List all categories
GET    /api/categories/<slug>/   # Category detail
```

### Reviews

```
GET    /api/reviews/             # List reviews
POST   /api/reviews/             # Create review (authenticated)
GET    /api/reviews/<id>/        # Review detail
PUT    /api/reviews/<id>/        # Update review (owner)
DELETE /api/reviews/<id>/        # Delete review (owner)
GET    /api/reviews/my_reviews/  # Current user's reviews
```

## Models

### CustomUser
- Extended Django AbstractUser
- User types: Customer, Service Provider
- Profile fields: phone, avatar, bio, city, state, zip_code
- Properties: is_provider, is_customer, has_provider_profile, full_name

### ServiceCategory
- name, slug, description, icon, image

### ServiceProvider
- Basic: name, slug, description, tagline
- Category & Skills
- Contact: email, phone, website
- Location: address, city, state, zip_code
- Business: pricing_range, years_experience
- Media: image, logo
- Status: is_verified, is_active, is_featured, is_draft
- Approval: approval_status (draft, approved, rejected, suspended), approved_at, submitted_for_review_at
- Emergency: is_available_now, accepts_emergency, emergency_rate_info
- Computed: average_rating, review_count, completion_percentage
- Methods: can_submit(), calculate_completion_percentage()

### ProviderReview
- user, provider (FK)
- rating (1-5), title, comment
- would_recommend, service_date
- helpful_count

### FavoriteProvider
- user, provider (FK)
- Timestamp tracking

### ProviderImage
- provider (FK), image, caption, alt_text
- is_featured, order
- Gallery/portfolio images for providers

### QuoteRequest
- user, provider (FK)
- Request: title, description, timeline, budget
- Contact: preferred_contact, phone
- Location: service_address, service_city, service_zip
- Status: pending, viewed, quoted, accepted, declined, expired
- Provider Response: quote_amount, quote_message, quoted_at
- is_emergency flag for urgent requests

### BusinessHours
- provider (OneToOne FK)
- Monday-Sunday: open, close, closed (for each day)
- notes (additional availability information)

### ServiceArea
- provider (FK)
- zip_code, city, state
- radius_miles (service radius in miles)
- is_primary (primary service location flag)
- created_at

### ProviderCertification
- provider (FK)
- name, issuing_organization, license_number
- issue_date, expiry_date
- verification_document (file upload)
- is_verified (admin verified flag)
- created_at, updated_at
- Property: is_expired (checks expiry date)

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DEBUG | Debug mode | True |
| SECRET_KEY | Django secret key | (generate one) |
| ALLOWED_HOSTS | Allowed hosts | localhost,127.0.0.1 |
| POSTGRES_DB | Database name | findapro |
| POSTGRES_USER | Database user | findapro_user |
| POSTGRES_PASSWORD | Database password | findapro_password |
| POSTGRES_HOST | Database host | db (Docker) / localhost |
| POSTGRES_PORT | Database port | 5432 |

## Adding Sample Data

### Quick Setup (Recommended)

Populate the database with realistic mock data using the built-in command:

```bash
docker-compose exec web python manage.py populate_data
```

This creates:
- **10 Service Categories** (Plumbing, Electrical, Cleaning, HVAC, etc.)
- **10 Mock Users** (username: `john_doe`, `jane_smith`, etc. / password: `password123`)
- **13 Service Providers** with realistic details and descriptions
- **40-70 Reviews** randomly distributed across providers
- **Emergency-ready providers** with availability settings
- **Sample quote requests** (if applicable)

Note: Gallery images need to be added manually through the Django Admin panel.

### Reset Data

To reset and repopulate:

```bash
docker-compose exec web python manage.py flush --noinput
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py populate_data
```

### Manual Data Entry

You can also add data manually through:

1. **Django Admin** (http://localhost:8000/admin)
   - Login with `admin` / `adminpassword`
   - Add categories first, then providers
   - Reviews are added by registered users

2. **Django Shell** - For custom data scripting:
```bash
docker-compose exec web python manage.py shell
```

## Troubleshooting

### Docker credential error on Mac
If you see `docker-credential-desktop: executable file not found`:
```bash
# Edit Docker config to remove credential helper
echo '{"auths": {}, "currentContext": "desktop-linux"}' > ~/.docker/config.json
```

### Container not starting
Check logs for errors:
```bash
docker-compose logs web
```

### Database connection issues
Ensure PostgreSQL is healthy:
```bash
docker-compose ps  # Should show "healthy" for db
```

### TailwindCSS not building
Rebuild CSS manually:
```bash
docker-compose exec web npm run build:css
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - feel free to use this project for learning or as a starting point for your own marketplace.

