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
- **Multi-Mode Profiles** - Users can operate in multiple modes simultaneously: Service Provider, Freelance, and Skill Swap
- **Freelance Mode** - Project-based work and digital services with portfolio showcase, hourly/project pricing, and skills tags
- **Skill Swap Mode** - Bartering system with skills offered/wanted, credit system (1 hour = 1 credit), and swap-specific profiles
- **Smart Matching Algorithm** - AI-powered matching system that connects users for skill swaps and freelance collaborations based on compatibility scores
- **Time-Banking Credit System** - Comprehensive credit economy with escrow, automatic transfers, welcome bonuses, and transaction history
- **Unified Booking/Request System** - Single interface for paid jobs, credit-based swaps, and barter proposals with proposal/counter-offer negotiation, unified messaging, and integrated payment processing
- **Skill Analytics Dashboard** - Visual analytics showing skill supply and demand in local areas with heat maps, trending skills, opportunity identification, and personalized recommendations
- **Community Project Board** - Multi-person collaborative project system with role-based applications, team coordination, milestone tracking, file sharing, and badge/achievement system

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

### Multi-Mode Profile Routes
- `/accounts/modes/` - Profile modes dashboard (manage all modes)
- `/accounts/modes/toggle/` - Toggle mode activation
- `/accounts/modes/set-active/` - Set active mode for UI context
- `/accounts/freelance/` - Browse freelance listings
- `/accounts/freelance/create/` - Create freelance listing
- `/accounts/freelance/<id>/` - Freelance listing detail
- `/accounts/freelance/<id>/edit/` - Edit freelance listing
- `/accounts/freelance/<id>/portfolio/` - Manage portfolio items
- `/accounts/skill-swap/` - Browse skill swap listings
- `/accounts/skill-swap/create/` - Create skill swap listing
- `/accounts/skill-swap/<id>/` - Skill swap listing detail
- `/accounts/skill-swap/<id>/edit/` - Edit skill swap listing
- `/accounts/credits/` - View skill credits (earned/spent) - Legacy
- `/accounts/credits/create/` - Record a skill swap credit transaction - Legacy
- `/accounts/credits/<id>/approve/` - Approve pending credit - Legacy

### Credit System Routes
- `/accounts/credits/dashboard/` - Credit dashboard with balance, history, and statistics
- `/accounts/credits/history/` - Filtered transaction history
- `/accounts/credits/transaction/<id>/` - Transaction detail view
- `/accounts/credits/job/<job_id>/confirm/` - Confirm job completion to release escrow

### Unified Job System Routes
- `/providers/jobs/` - Unified job dashboard (all jobs: paid/credit/barter)
- `/providers/jobs/create/provider/<slug>/` - Create job request for a provider
- `/providers/jobs/create/user/<user_id>/` - Create job request for a user (skill swap)
- `/providers/jobs/<id>/` - Job detail with proposals and messaging
- `/providers/jobs/<job_id>/proposal/` - Submit a proposal/counter-offer
- `/providers/jobs/<job_id>/message/` - Send message in job thread
- `/providers/jobs/<job_id>/confirm/` - Confirm job completion
- `/proposals/<proposal_id>/accept/` - Accept a proposal
- `/proposals/<proposal_id>/decline/` - Decline a proposal

### Skill Analytics Routes
- `/providers/analytics/` - Skill analytics dashboard with supply/demand visualization

### Community Project Routes
- `/providers/projects/` - Browse community projects
- `/providers/projects/create/` - Create a new project
- `/providers/projects/<id>/` - View project details and apply for roles
- `/providers/projects/<id>/manage/` - Project management dashboard (creator/leads only)
- `/providers/projects/<project_id>/publish/` - Publish draft project
- `/applications/<application_id>/accept/` - Accept an application
- `/applications/<application_id>/decline/` - Decline an application
- `/providers/projects/<project_id>/milestone/` - Create project milestone
- `/providers/projects/<project_id>/message/` - Send team message

### Smart Matching Routes
- `/accounts/matches/` - Match suggestions page (top 10 compatible users)
- `/accounts/matches/my-matches/` - View all matches and connections
- `/accounts/matches/<id>/` - Match detail view with compatibility breakdown
- `/accounts/matches/<id>/interested/` - Mark match as interested
- `/accounts/matches/<id>/not-interested/` - Hide match from suggestions
- `/accounts/matches/refresh/` - Regenerate matches

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
│   ├── accounts/      # Custom user model, authentication, multi-mode profiles, matching, credits
│   │   ├── modes_models.py      # FreelanceListing, SkillSwapListing, SkillSwapJob, SkillCredit models
│   │   ├── modes_views.py        # Multi-mode profile views
│   │   ├── modes_forms.py       # Multi-mode forms
│   │   ├── matching_models.py    # Match, MatchHistory models
│   │   ├── matching_service.py  # Smart matching algorithm
│   │   ├── matching_views.py     # Match suggestion views
│   │   ├── credit_service.py     # Credit transaction service
│   │   ├── credit_signals.py     # Automatic credit management signals
│   │   ├── credit_views.py       # Credit dashboard views
│   │   └── management/commands/ # send_match_notifications command
│   ├── providers/     # Service providers, categories, search, unified jobs, analytics, projects
│   │   ├── unified_jobs.py        # UnifiedJob, JobProposal, JobMessage models
│   │   ├── unified_job_forms.py   # Unified job request and proposal forms
│   │   ├── unified_job_views.py   # Unified job dashboard and detail views
│   │   ├── skill_analytics.py     # SkillDemand, SkillSupply, SkillMarketOpportunity models
│   │   ├── analytics_service.py   # Skill analytics calculation service
│   │   ├── analytics_views.py     # Skill analytics dashboard views
│   │   ├── community_projects.py  # CommunityProject, ProjectRole, ProjectApplication, etc.
│   │   ├── project_forms.py       # Project creation and application forms
│   │   ├── project_views.py       # Project browsing, creation, management views
│   │   ├── project_recommendations.py  # Project-skill matching service
│   │   ├── user_badges.py        # UserBadge, UserBadgeAward models and service
│   │   └── management/commands/   # update_skill_analytics command
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

### 🔄 Multi-Mode Profile System
Users can now operate in multiple modes simultaneously, allowing them to be a service provider, freelancer, and skill swapper all at once:

**Three Operating Modes:**

1. **Service Provider Mode** (Original)
   - Traditional Angie's List-style business profiles
   - Categories, skills, reviews, ratings
   - Business hours, service areas, certifications

2. **Freelance Mode** - For project-based work and digital services
   - **Portfolio Showcase**: Upload images, links, and case studies
   - **Pricing**: Set hourly rates and/or project-based pricing
   - **Skills & Expertise**: Tag skills and expertise areas
   - **Availability Calendar**: Set availability status and timezone
   - **Portfolio Links**: GitHub, LinkedIn, Behance, portfolio website
   - **Project Proposals**: Ready for bidding/proposal system integration

3. **Skill Swap Mode** - For bartering services
   - **Skills Offered**: ManyToMany relationship with reusable Skill model
   - **Skills Wanted**: ManyToMany relationship for desired skills
   - **Credit System**: Time-banking (1 hour = 1 credit)
   - **Credit Tracking**: Earned/spent credits with approval workflow
   - **Swap-Specific Bio**: Dedicated description for skill swapping
   - **Location Preferences**: Remote/local preferences for swaps

**Key Features:**
- **Unified Dashboard**: Manage all modes from one central location (`/accounts/modes/`)
- **Mode Activation**: Toggle modes on/off independently
- **Active Mode Selection**: Choose which mode to display in UI context
- **Independent Listings**: Each mode has its own listing/profile
- **Simultaneous Operation**: Be active in all three modes at once
- **Mode-Specific Navigation**: UI adapts based on active mode

**URLs**: 
- Dashboard: `/accounts/modes/`
- Freelance: `/accounts/freelance/`
- Skill Swap: `/accounts/skill-swap/`
- Credits: `/accounts/credits/`

### 🤝 Smart Matching Algorithm
AI-powered matching system that connects users for skill swaps and freelance collaborations:

**Matching Logic:**
- Finds users where Person A's "skills_offered" match Person B's "skills_wanted" (and vice versa)
- Calculates compatibility score (0-100%) based on:
  - **Skill Overlap** (40-50% weight): Percentage of matching skills
  - **Geographic Proximity** (20% weight): City/state/zip code similarity
  - **Reputation Score** (20% weight): Ratings, reviews, verification status
  - **Availability Alignment** (10-20% weight): Availability status and preferences

**Match Suggestions:**
- **Top 10 Compatible Users**: Ranked by compatibility score
- **Match Breakdown**: See why you're a match (which skills align)
- **Filter by Mode**: View skill swap matches or freelance collaboration matches separately
- **Connect Button**: Express interest to initiate contact
- **Match History**: Track all matches and connections

**Match Management:**
- **Mark Interested**: Show interest in a match
- **Mutual Interest**: Automatic connection when both users are interested
- **Not Interested**: Hide specific matches from suggestions
- **Match History**: View all past matches with status tracking
- **Refresh Matches**: Regenerate matches with updated data

**Notifications:**
- **Weekly Email Digest**: "You have X new potential matches" email
- **Management Command**: `python manage.py send_match_notifications`
- **In-App Notifications**: New matches indicator in UI
- **Configurable**: Set number of days to look back for new matches

**Match Statuses:**
- `pending` - New match, not yet viewed
- `viewed` - Match has been viewed
- `interested` - User expressed interest
- `connected` - Both users are interested (mutual match)
- `not_interested` - User marked as not interested (hidden)

**URLs**: 
- Suggestions: `/accounts/matches/`
- My Matches: `/accounts/matches/my-matches/`
- Match Detail: `/accounts/matches/<id>/`
- Refresh: `/accounts/matches/refresh/`

**Management Command:**
```bash
# Send weekly match notifications
docker-compose exec web python manage.py send_match_notifications

# Dry run to preview
docker-compose exec web python manage.py send_match_notifications --dry-run

# Custom lookback period (default: 7 days)
docker-compose exec web python manage.py send_match_notifications --days=14
```

### 📋 Unified Booking/Request System

A comprehensive unified job/booking system that handles paid jobs, credit-based skill swaps, and barter proposals through a single interface. This system replaces the need for separate quote request and skill swap job flows, providing a consistent experience across all job types.

**Three Payment Types:**

1. **Paid Jobs** 💰
   - Standard payment-based service requests
   - Budget range specification (min/max)
   - Agreed amount negotiation through proposals
   - Payment processing integration ready

2. **Credit-Based Swaps** 🔄
   - Time-banking credit system integration
   - Credits requested/agreed (hours)
   - Automatic escrow creation and release
   - Links to SkillSwapJob for credit processing

3. **Barter Proposals** 🤝
   - Service-for-service exchanges
   - "I'll do X for you if you do Y for me"
   - Negotiable terms through proposals
   - No monetary or credit exchange

**Key Features:**

- **Unified Job Request Form** - Single form with conditional fields based on payment type
- **Proposal & Counter-Offer System** - Providers can submit proposals, requesters can accept/decline or counter
- **Unified Messaging Thread** - Dedicated message thread per job for communication
- **Job Management Dashboard** - View all jobs (paid/credit/barter) in one place with filtering
- **Status Tracking** - Track jobs through: pending → proposed → accepted → in_progress → completed
- **Completion Confirmation** - Both parties must confirm completion before payment/credits release
- **Provider Preferences** - Providers can specify which job types they accept (paid/credits/barter)
- **Search Filters** - Filter providers by job acceptance preferences
- **Provider Badges** - Visual indicators: "Accepts Credits", "Open to Barter", "Paid Only"

**Job Flow:**

1. **Request Creation** - Requester creates job with payment type and details
2. **Proposal Submission** - Provider submits initial proposal or counter-offer
3. **Proposal Acceptance** - Requester accepts proposal → Job status changes to "accepted"
4. **Job Execution** - Status changes to "in_progress" when work begins
5. **Completion Confirmation** - Both parties confirm completion
6. **Payment/Credit Processing** - Automatic processing based on payment type:
   - Paid: Payment processed (integration ready)
   - Credit: Escrow released, credits transferred
   - Barter: Exchange completed

**Proposal Types:**

- **Initial Proposal** - First proposal from provider
- **Counter Offer** - Subsequent proposals with modified terms
- **Acceptance** - Requester accepts proposal
- **Decline** - Requester declines proposal

**Integration:**

- **Credit System** - Seamlessly integrates with existing credit escrow system
- **Skill Swap Jobs** - Automatically creates SkillSwapJob for credit-based jobs
- **Provider Profiles** - Respects provider job acceptance preferences
- **Search & Discovery** - Enhanced search with job type filters

**URLs**: 
- Dashboard: `/providers/jobs/`
- Create (Provider): `/providers/jobs/create/provider/<slug>/`
- Create (User): `/providers/jobs/create/user/<user_id>/`
- Detail: `/providers/jobs/<id>/`

**Admin Features:**
- View all jobs with filtering by type and status
- Mark jobs as completed
- Cancel jobs
- Process payments
- View proposals and messages
- Resolve disputes

### 📊 Skill Analytics Dashboard

A comprehensive visual analytics system that tracks skill supply and demand in local geographic areas, helping users identify market opportunities, trending skills, and make data-driven decisions about their skill development.

**Key Features:**

- **Demand Calculation** - Analyzes job requests and skill swap wants to calculate demand scores
- **Supply Calculation** - Tracks providers, skill swap offers, and freelance listings for supply scores
- **Market Opportunities** - Identifies high-opportunity skills (high demand, low supply)
- **Trending Skills** - Tracks skills with increasing demand over time
- **Personalized Insights** - Provides actionable recommendations based on user's skills
- **Visual Analytics** - Interactive charts using Chart.js (bar, line, radar charts)
- **Geographic Filtering** - Filter by city, state, ZIP code, and radius
- **Skill Recommendations** - Suggests complementary skills to learn with swap opportunities

**Analytics Models:**

- **SkillDemand** - Tracks demand scores by skill and location with trend analysis
- **SkillSupply** - Tracks supply scores by skill and location with trend analysis
- **SkillMarketOpportunity** - Aggregated view showing demand vs supply ratios and market status

**Market Status Types:**

- **High Opportunity** - High demand, low supply (perfect for new providers)
- **Balanced** - Demand and supply are roughly equal
- **Oversupplied** - Low demand, high supply (good for skill swapping)
- **Emerging** - Low demand, low supply (early market)

**Visualizations:**

- **Top Opportunities Chart** - Bar chart showing top 10 skills with high opportunity scores
- **Trending Skills Chart** - Line chart showing skills with increasing demand
- **Your Skills Radar Chart** - Radar chart comparing your skills' demand vs supply

**Personalized Insights:**

- "Your photography skills are in high demand! Consider raising your rates."
- "Learn videography - demand has increased by 87% in your area!"
- "5 people near you want to learn what you offer"

**Management Command:**

Update analytics daily via scheduled task:
```bash
docker compose exec web python manage.py update_skill_analytics

# Options:
# --days-back=30    Number of days to analyze (default: 30)
# --city=San Francisco    Filter by specific city
# --state=CA    Filter by specific state
# --skill=photography    Filter by specific skill slug
# --radius=25    Radius in miles (default: 25)
```

**URL**: `/providers/analytics/`

### 🏗️ Community Project Board

A comprehensive system for creating and managing multi-person collaborative projects. Perfect for community initiatives, creative collaborations, business ventures, and learning projects.

**Project Types:**

1. **Community Projects** 🏘️
   - Neighborhood improvements
   - Charity work
   - Local initiatives

2. **Creative Collaborations** 🎨
   - Film production
   - Events planning
   - Art installations
   - Content creation

3. **Business Ventures** 💼
   - Startup teams
   - Co-working opportunities
   - Business partnerships

4. **Learning Projects** 📚
   - Group learning
   - Mentorship circles
   - Skill-building initiatives

**Key Features:**

- **Multi-Role Projects** - Define multiple roles needed (e.g., "Need: 1 electrician, 1 carpenter, 1 designer")
- **Role Application System** - Users browse and apply for specific roles with cover letters
- **Application Review** - Project creators review applicants and accept/decline
- **Team Management** - Track team members, assign roles, designate leads
- **Milestone Tracking** - Create and track project milestones with assignments
- **Team Messaging** - Unified discussion thread for team coordination
- **File Sharing** - Share plans, designs, documents within projects
- **Status Updates** - Track project status: draft → recruiting → in_progress → completed
- **Skill-Based Recommendations** - "Projects you'd be great for" based on your skills
- **Badge System** - Earn badges: Community Builder, Collaborator, Project Leader, Volunteer
- **Project Showcase** - Completed projects displayed on user profiles

**Project Creation Flow:**

1. **Create Project** - Fill in title, description, type, timeline, location
2. **Define Roles** - Add multiple roles with skill requirements, time commitment, compensation
3. **Publish** - Make project visible to community (or keep as draft)
4. **Review Applications** - Review and accept/decline applications for each role
5. **Build Team** - Once roles filled, project moves to "in_progress"
6. **Manage Project** - Track milestones, coordinate via messages, share files
7. **Complete** - Mark project as completed when finished

**Role Application Flow:**

1. **Browse Projects** - Filter by type, location, compensation
2. **View Open Roles** - See available roles and requirements
3. **Apply** - Submit cover letter and relevant experience
4. **Wait for Review** - Project creator reviews application
5. **Get Accepted** - Join team and start collaborating

**Compensation Types:**

- **Paid** - Monetary compensation
- **Credits** - Time-banking credits
- **Volunteer** - No compensation (community service)
- **Mixed** - Combination of above

**Badge System:**

- **Community Builder** 🏗️ - Created 3+ projects
- **Collaborator** 🤝 - Participated in 5+ projects
- **Project Leader** 👑 - Led 2+ projects to completion
- **Volunteer** ❤️ - Participated in 3+ volunteer projects

Badges are automatically awarded based on activity and displayed on user profiles.

**Team Coordination:**

- **Milestones** - Break project into manageable tasks with due dates
- **Messages** - Team discussion thread with pinning support
- **Files** - Share documents, images, designs, plans
- **Status Updates** - Real-time project status visible to all members

**Discovery Features:**

- **Recommendations** - See projects matching your skills
- **Filters** - By type, location, compensation, timeline
- **Featured Projects** - Highlighted community projects
- **Search** - Find projects by keywords

**URLs**: 
- Browse: `/providers/projects/`
- Create: `/providers/projects/create/`
- Detail: `/providers/projects/<id>/`
- Manage: `/providers/projects/<id>/manage/`

**How to Use:**

1. **Create a Project**
   - Click "Create Project" from project list
   - Fill in project details and add roles
   - Save as draft or publish immediately

2. **Apply for Roles**
   - Browse projects and find roles that match your skills
   - Click "Apply for This Role"
   - Submit cover letter and relevant experience

3. **Manage Your Project**
   - Go to project detail page
   - Click "Manage Project" (creator/leads only)
   - Review applications, create milestones, coordinate team

4. **Track Progress**
   - Use milestones to break down work
   - Use team messages for coordination
   - Upload files for sharing plans/documents

**How to Use:**

1. **Access Dashboard** - Click "Skill Analytics" in user dropdown menu
2. **Set Location** - Use filters to set your city, state, and ZIP code
3. **View Opportunities** - See top skills with high demand and low supply
4. **Check Trends** - Identify skills with increasing demand
5. **Review Your Skills** - See how your skills compare to market demand
6. **Get Recommendations** - Find complementary skills to learn
7. **Update Analytics** - Run management command daily for fresh data

**How to Use:**

### For Requesters (Customers):

1. **Finding a Provider**
   - Browse providers at `/providers/` or search by category/skill
   - Look for badges indicating job acceptance: "Accepts Credits" 🔄, "Open to Barter" 🤝, or "Paid Only" 💰
   - Click on a provider profile to view details

2. **Creating a Job Request**
   - From provider detail page, click **"Request Job"** button
   - Or navigate to `/providers/jobs/create/provider/<provider-slug>/`
   - Select job type:
     - **Paid Job**: Enter budget range (min/max)
     - **Credit Swap**: Enter credits requested (hours, e.g., 2.5 = 2.5 hours)
     - **Barter**: Enter what you offer and what you want
   - Fill in job details:
     - Title (e.g., "Kitchen sink repair")
     - Description (detailed work description)
     - Timeline (ASAP, this week, next week, etc.)
     - Service location (address, city, state, ZIP)
     - Contact preferences
   - Submit the request

3. **Managing Your Jobs**
   - Go to **"My Jobs"** in the user dropdown menu (`/providers/jobs/`)
   - View all your jobs (as requester or provider)
   - Filter by status (pending, in progress, completed) or type (paid, credit, barter)
   - See statistics: total jobs, pending, in progress, completed

4. **Responding to Proposals**
   - When a provider submits a proposal, you'll see it on the job detail page
   - Review the proposal terms:
     - Paid: Proposed amount
     - Credit: Proposed credits (hours)
     - Barter: Proposed exchange terms
   - Options:
     - **Accept**: Job status changes to "accepted", work can begin
     - **Decline**: Proposal is declined, provider can submit another
     - **Counter**: Provider can submit a counter-offer

5. **Completing a Job**
   - Once work is done, go to the job detail page
   - Click **"Confirm Completion"**
   - Both parties must confirm
   - Once both confirm:
     - **Paid**: Payment is processed
     - **Credit**: Credits are automatically transferred from escrow
     - **Barter**: Exchange is marked complete

### For Providers:

1. **Setting Job Acceptance Preferences**
   - Go to your provider profile edit page (`/providers/profile/edit/`)
   - In "Job Acceptance Preferences" section:
     - ✅ Accept Paid Jobs (default: enabled)
     - ✅ Accept Credit Jobs (enable if you want credit-based swaps)
     - ✅ Accept Barter (enable if you're open to barter proposals)
   - Save your preferences
   - These preferences appear as badges on your profile

2. **Receiving Job Requests**
   - Job requests appear in your job dashboard (`/providers/jobs/`)
   - Filter to see jobs where you're the provider
   - Click on a job to view details

3. **Submitting Proposals**
   - On the job detail page, you'll see a "Submit Proposal" form
   - Enter your proposal:
     - **Message**: Explain your proposal and terms
     - **Terms** (based on job type):
       - Paid: Proposed amount ($)
       - Credit: Proposed credits/hours
       - Barter: What you offer and what you want
   - Submit the proposal
   - The requester can accept, decline, or you can submit a counter-offer

4. **Negotiating Terms**
   - If your initial proposal is declined, you can submit a counter-offer
   - Modify your terms and resubmit
   - Continue negotiating until terms are agreed or declined

5. **Completing Work**
   - Once proposal is accepted, job status changes to "in_progress"
   - Complete the work as agreed
   - When finished, go to job detail page
   - Click **"Confirm Completion"**
   - Wait for requester to confirm
   - Once both confirm, payment/credits are processed automatically

### Messaging System:

- **Unified Thread**: Each job has its own message thread
- **Send Messages**: Use the message form at the bottom of job detail page
- **Read Status**: Messages show read/unread status
- **Notifications**: Messages are linked to proposals when relevant

### Example Workflows:

**Example 1: Paid Job**
1. Customer requests "Plumbing repair" as paid job ($200-300 budget)
2. Provider submits proposal: $250
3. Customer accepts → Job status: "accepted"
4. Provider completes work
5. Both confirm completion → Payment processed

**Example 2: Credit Swap**
1. User requests "Logo design" as credit job (3 credits)
2. Provider submits proposal: 3 credits
3. Customer accepts → Credits held in escrow, job status: "accepted"
4. Provider completes design
5. Both confirm completion → 3 credits transferred from customer to provider

**Example 3: Barter**
1. User requests "I'll write your website copy if you design my logo"
2. Provider submits proposal: "I'll design your logo if you write my website copy"
3. Customer accepts → Job status: "accepted"
4. Both complete their parts
5. Both confirm completion → Barter exchange complete

### Tips:

- **Check Provider Preferences**: Before requesting, check if provider accepts your preferred payment type
- **Be Specific**: Detailed job descriptions get better proposals
- **Respond Promptly**: Quick responses keep the negotiation moving
- **Use Messages**: Communicate any questions or clarifications through the job message thread
- **Review Terms**: Carefully review proposal terms before accepting
- **Confirm Completion**: Always confirm completion to release payment/credits

### 💰 Time-Banking Credit System
Comprehensive credit economy for skill swaps with escrow, automatic transfers, and transaction tracking:

**Credit Economy:**
- **1 Hour = 1 Credit**: Standardized time-banking system regardless of skill type
- **Welcome Bonus**: New users receive 5 bonus credits when creating a skill swap listing
- **Balance Tracking**: Real-time balance calculation (earned - spent)
- **Available Balance**: Balance minus credits held in escrow
- **Negative Balance Prevention**: System prevents spending more credits than available

**Transaction Types:**
- `earned` - Credits earned by providing services
- `spent` - Credits spent to receive services
- `bonus` - Welcome bonus or promotional credits
- `adjustment` - Admin manual adjustments
- `refund` - Refunded credits (e.g., cancelled jobs)
- `escrow_hold` - Credits held in escrow for pending jobs
- `escrow_release` - Credits released from escrow

**Job Completion Flow:**
1. **Requester posts job** → Credits automatically held in escrow
2. **Provider accepts** → Job moves to "in progress"
3. **Both parties confirm completion** → Credits automatically transferred:
   - Provider receives earned credits
   - Requester's spent credits deducted
   - Escrow released
4. **Job cancelled** → Escrow automatically refunded to requester

**Credit Dashboard Features:**
- **Balance Cards**: Total balance, available balance, escrow amount, net change
- **30-Day Summary**: Credits earned vs spent with net change
- **Pending Jobs**: List of jobs with credits in escrow
- **Transaction History**: Complete ledger with filtering and sorting
- **Transaction Details**: Full details of each credit transaction
- **Completion Confirmation**: Easy job completion confirmation interface

**Escrow System:**
- Credits held securely until job completion
- Automatic hold when job is posted
- Automatic release when both parties confirm
- Automatic refund on cancellation
- Prevents double-spending

**Admin Features:**
- **Manual Adjustments**: Admin can add/subtract credits with notes
- **Dispute Resolution**: Handle disputes and adjust credits accordingly
- **Job Management**: Mark jobs as completed, cancel jobs, resolve disputes
- **Transaction Approval**: Approve/reject pending transactions
- **Credit Expiration**: Optional credit expiration dates

**Automatic Features:**
- Welcome bonus awarded on skill swap listing creation
- Escrow created automatically when job posted
- Credits transferred automatically on completion confirmation
- Escrow refunded automatically on cancellation
- Balance updates automatically on transaction approval

**URLs**: 
- Dashboard: `/accounts/credits/dashboard/`
- History: `/accounts/credits/history/`
- Transaction Detail: `/accounts/credits/transaction/<id>/`
- Confirm Completion: `/accounts/credits/job/<job_id>/confirm/`

**Usage Example:**
```python
from apps.accounts.credit_service import CreditTransactionService

# Get user balance
balance = CreditTransactionService.get_user_balance(user)
available = CreditTransactionService.get_available_balance(user)

# Award bonus credits
CreditTransactionService.award_bonus_credits(user, credits=5)

# Create escrow for job
success, error, escrow = CreditTransactionService.create_escrow_hold(job)

# Release escrow on completion
success, error = CreditTransactionService.release_escrow(job)

# Admin adjustment
CreditTransactionService.admin_adjustment(user, credits=10, description="Promotion", admin_user=admin)
```

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
- Multi-mode fields: is_freelancer_active, is_skill_swap_active, active_mode
- Properties: 
  - is_provider, is_customer, has_provider_profile, full_name
  - has_freelance_listing, has_skill_swap_listing
  - active_modes (list of active modes)
  - total_skill_credits (sum of credit balance)

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

### Multi-Mode Profile Models

#### Skill
- Reusable skill tags for freelance and skill swap modes
- name, slug, category, description, icon
- is_active flag

#### FreelanceListing
- OneToOne relationship with CustomUser
- title, bio, skills (ManyToMany), expertise_tags
- hourly_rate, project_rate_min/max, currency
- portfolio_url, github_url, linkedin_url, behance_url
- availability_status, availability_notes, timezone
- is_active, is_featured, is_verified
- Property: skills_list (returns list of skills)

#### FreelancePortfolioItem
- portfolio items for freelance listings
- listing (FK), item_type (image/link/case_study)
- title, description, image, url
- order, created_at

#### SkillSwapListing
- OneToOne relationship with CustomUser
- bio, skills_offered (ManyToMany), skills_wanted (ManyToMany)
- additional_skills_offered, additional_skills_wanted
- credits_earned, credits_spent
- accepts_remote, location_preference
- is_active, is_verified
- Properties: skills_offered_list, skills_wanted_list, credits_balance

#### SkillSwapJob
- Tracks skill swap jobs from request to completion
- requester, provider (FK)
- title, description, skill_needed (FK)
- hours_required (credits required)
- status (posted/accepted/in_progress/completed/cancelled/disputed)
- requester_confirmed, provider_confirmed flags
- credits_in_escrow (credits held until completion)
- posted_at, accepted_at, started_at, completed_at, cancelled_at
- dispute_reason, dispute_resolved_by, dispute_resolved_at
- Properties: credits_required, is_completed

#### SkillCredit
- Credit transactions for skill swaps (time-banking: 1 hour = 1 credit)
- from_user, to_user (FK, from_user nullable for system transactions)
- job (FK, optional) - Links to SkillSwapJob
- transaction_type (earned/spent/bonus/adjustment/refund/escrow_hold/escrow_release)
- credits (Decimal, hours)
- skill_swapped (FK, optional)
- description, swap_date (optional)
- status (pending/approved/rejected/cancelled)
- verified_by, verified_at
- admin_notes (for admin adjustments)
- expires_at (optional credit expiration)
- Auto-updates SkillSwapListing credits upon approval
- Properties: is_expired

### Unified Job System Models

#### UnifiedJob
- Unified job model supporting paid, credit-based, and barter proposals
- requester, provider (FK, provider set when accepted)
- payment_type (paid/credit/barter)
- title, description, timeline, is_emergency
- service_address, service_city, service_state, service_zip
- Payment fields: budget_min, budget_max, agreed_amount (for paid jobs)
- Credit fields: credits_requested, credits_agreed, credits_in_escrow
- Barter fields: barter_offer, barter_request
- status (pending/proposed/accepted/declined/in_progress/completed/cancelled/disputed)
- requester_confirmed, provider_confirmed flags
- payment_processed, payment_processed_at
- preferred_contact, phone
- dispute_reason, dispute_resolved_by, dispute_resolved_at
- related_quote_request (FK, optional) - Links to QuoteRequest if converted
- related_skill_swap_job (FK, optional) - Links to SkillSwapJob for credit processing
- Timestamps: created_at, updated_at, accepted_at, started_at, completed_at, cancelled_at
- Properties: is_completed, has_pending_proposals, get_current_proposal()

#### JobProposal
- Proposals and counter-offers for job negotiations
- job (FK) - Links to UnifiedJob
- proposed_by (FK) - User making the proposal
- proposal_type (initial/counter/accept/decline)
- status (pending/accepted/declined/expired)
- message - Proposal message text
- Payment terms: proposed_amount (for paid jobs)
- Credit terms: proposed_credits (for credit jobs)
- Barter terms: proposed_barter_offer, proposed_barter_request
- response_message, responded_at
- expires_at (optional expiration)
- Properties: is_expired

#### JobMessage
- Unified messaging thread for job discussions
- job (FK) - Links to UnifiedJob
- sender, recipient (FK)
- message - Message text
- is_read, read_at
- related_proposal (FK, optional) - Links to JobProposal if message is about a proposal
- created_at
- Methods: mark_as_read()

#### ServiceProvider (Enhanced)
- New fields: accepts_paid_jobs, accepts_credit_jobs, accepts_barter
- Allows providers to specify which job types they accept
- Used for filtering in search and displaying badges

### Skill Analytics Models

#### SkillDemand
- Tracks demand for skills by geographic area
- skill (FK), city, state, zip_code, radius_miles
- demand_score (calculated score)
- job_requests_count, skill_swap_wants_count, total_demand_signals
- previous_demand_score, demand_change_percent (trend tracking)
- period_start, period_end, calculated_at
- Properties: is_trending_up, trend_direction

#### SkillSupply
- Tracks supply of skills by geographic area
- skill (FK), city, state, zip_code, radius_miles
- supply_score (calculated score)
- provider_count, skill_swap_offers_count, freelance_listings_count, total_supply_signals
- previous_supply_score, supply_change_percent (trend tracking)
- period_start, period_end, calculated_at
- Properties: is_trending_up

#### SkillMarketOpportunity
- Aggregated view of skill market opportunities (demand vs supply)
- skill (FK), city, state, zip_code
- demand_score, supply_score, opportunity_score
- market_status (high_opportunity/balanced/oversupplied/emerging)
- period_start, period_end, calculated_at
- Properties: demand_supply_ratio

### Community Project Models

#### CommunityProject
- Multi-person collaborative project
- creator (FK), title, description, project_type, status
- start_date, end_date, timeline_description
- location_city, location_state, location_address, location_zip, is_remote_friendly
- compensation_type, budget_total
- featured_image, is_featured
- view_count, application_count
- Timestamps: created_at, updated_at, published_at, started_at, completed_at
- Properties: total_roles, filled_roles, open_roles, is_recruiting, team_members

#### ProjectRole
- Role needed for a project
- project (FK), title, description
- skill_required (FK), skills_preferred (ManyToMany)
- time_commitment_hours, time_commitment_description, experience_level
- compensation_type, compensation_amount, compensation_description
- status (open/filled/closed), filled_by (FK), filled_at
- Properties: application_count

#### ProjectApplication
- Application for a project role
- role (FK), applicant (FK)
- cover_letter, relevant_experience
- status (pending/accepted/declined/withdrawn)
- reviewed_by (FK), reviewed_at, review_notes
- Unique constraint: one application per user per role

#### ProjectMember
- Team member of a project
- project (FK), user (FK), role (FK, nullable)
- role_title, is_creator, is_lead
- status (active/inactive/removed)
- joined_at, left_at
- Unique constraint: one membership per user per project

#### ProjectMilestone
- Project milestone/task
- project (FK), title, description, due_date
- status (not_started/in_progress/completed/blocked)
- assigned_to (ManyToMany), completed_by (FK), completed_at

#### ProjectFile
- File shared within a project
- project (FK), uploaded_by (FK), file
- file_type (document/image/design/plan/other)
- title, description
- milestone (FK, optional)

#### ProjectMessage
- Message in project team discussion
- project (FK), sender (FK), message
- is_pinned, milestone (FK, optional)
- created_at, updated_at

#### UserBadge
- Badge/achievement definition
- name, slug, badge_type, description, icon, image
- criteria (how to earn), is_active

#### UserBadgeAward
- Awarded badge to a user
- user (FK), badge (FK), awarded_at
- awarded_for_project (FK, optional), notes
- Unique constraint: one award per user per badge

### Smart Matching Models

#### Match
- Represents a potential match between two users
- user_a, user_b (FK)
- match_type (skill_swap/freelance_collab/both)
- compatibility_score (0-100%)
- Score breakdown: skill_overlap_percentage, geographic_proximity_score, reputation_score, availability_score
- matching_skills (JSONField): List of skills that match
- status (pending/viewed/interested/connected/not_interested/expired)
- user_a_interested, user_b_interested flags
- user_a_not_interested, user_b_not_interested flags
- connected_at, last_viewed_a, last_viewed_b timestamps
- Methods: mark_viewed(), mark_interested(), mark_not_interested()
- Properties: is_mutual_interest, is_connected

#### MatchHistory
- Track match history and prevent duplicate suggestions
- user, matched_user (FK)
- match (FK, optional)
- action (suggested/viewed/interested/not_interested/connected)
- notes, created_at

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

### Mock Data Generation (Recommended for Testing)

The app includes a comprehensive mock data generation command that creates realistic test data for all features:

**Using Docker (Recommended):**
```bash
# Load category fixtures
docker-compose exec web python manage.py loaddata apps/providers/fixtures/categories.json

# Load skill fixtures
docker-compose exec web python manage.py loaddata apps/accounts/fixtures/skills.json

# Generate default data (50 users, 30 jobs, 15 projects)
docker-compose exec web python manage.py generate_mock_data

# Customize quantities
docker-compose exec web python manage.py generate_mock_data --users=100 --jobs=50 --projects=20

# Clear existing data and regenerate
docker-compose exec web python manage.py generate_mock_data --clear

# Skip creating superuser (if already exists)
docker-compose exec web python manage.py generate_mock_data --skip-superuser
```

**Using Local Python (with virtual environment):**
```bash
# Activate your virtual environment first
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Load category fixtures
python manage.py loaddata apps/providers/fixtures/categories.json

# Load skill fixtures
python manage.py loaddata apps/accounts/fixtures/skills.json

# Generate default data (50 users, 30 jobs, 15 projects)
python manage.py generate_mock_data

# Customize quantities
python manage.py generate_mock_data --users=100 --jobs=50 --projects=20

# Clear existing data and regenerate
python manage.py generate_mock_data --clear

# Skip creating superuser (if already exists)
python manage.py generate_mock_data --skip-superuser
```

**What it generates:**
- **50-100 Users** with diverse profile types (Pro, Freelance, Swap, Hybrid)
- **30-50 Skill Swap Listings** with skills offered/wanted
- **30-50 Freelance Listings** with portfolio items
- **20-30 Provider Profiles** across all categories
- **30 Unified Jobs** (paid, credit-based, barter) with various statuses
- **15 Community Projects** with roles, applications, and team members
- **50-100 Credit Transactions** (earned, spent, bonuses)
- **50-100 Reviews** with varied ratings
- **20+ Matches** with compatibility scores
- **Superuser**: `admin` / `admin123` (unless skipped)

**Before running (if using Docker, prefix commands with `docker-compose exec web`):**
1. Load category fixtures:
   ```bash
   python manage.py loaddata apps/providers/fixtures/categories.json
   ```

2. Load skill fixtures:
   ```bash
   python manage.py loaddata apps/accounts/fixtures/skills.json
   ```

**Categories included:**
- Blue Collar Trades (Plumbing, Electrical, HVAC, Carpentry, etc.)
- Creative & Digital (Graphic Design, Web Dev, Photography, etc.)
- Professional Services (Accounting, Legal, Business Consulting, etc.)
- Wellness & Personal (Personal Training, Yoga, Nutrition, etc.)
- Events & Hospitality (Event Planning, Catering, DJ Services, etc.)
- Tech & IT (IT Support, Cybersecurity, App Development, etc.)

**Skills included:**
- 60+ skills mapped to categories
- Mix of hard skills (Python, Photoshop, Plumbing) and soft skills (Communication, Project Management)
- Realistic demand scores for analytics

### Quick Setup (Legacy)

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

