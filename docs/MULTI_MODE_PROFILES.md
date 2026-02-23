# Multi-Mode Profile System Documentation

## Overview

The FindAPro platform now supports **three distinct operating modes** that users can activate simultaneously:

1. **Service Provider Mode** - Traditional local services (existing)
2. **Freelance Mode** - Project-based work and digital services
3. **Skill Swap Mode** - Bartering services with time-banking credits

Users can have multiple modes active at once and switch between them seamlessly.

---

## Features

### 1. Freelance Mode

**Purpose**: For project-based work and digital services

**Key Features**:
- Professional title and bio
- Skills and expertise tags (ManyToMany with Skill model)
- Flexible pricing: hourly rate, project-based, or both
- Portfolio showcase: images, links, case studies
- Portfolio links: GitHub, LinkedIn, Behance/Dribbble
- Availability calendar and status
- Timezone support

**Models**:
- `FreelanceListing` - Main listing
- `FreelancePortfolioItem` - Portfolio items (images, links, case studies)

**URLs**:
- `/accounts/freelance/` - Browse all freelancers
- `/accounts/freelance/create/` - Create listing
- `/accounts/freelance/<id>/` - View listing
- `/accounts/freelance/<id>/edit/` - Edit listing
- `/accounts/freelance/<id>/portfolio/` - Manage portfolio

### 2. Skill Swap Mode

**Purpose**: Bartering services with time-banking system

**Key Features**:
- Skills offered (ManyToMany)
- Skills wanted (ManyToMany)
- Additional skills (text fields for flexibility)
- Credit system: 1 hour = 1 credit
- Credit balance tracking (earned - spent)
- Location preferences (local or remote)
- Swap transaction tracking

**Models**:
- `SkillSwapListing` - Main listing
- `SkillCredit` - Credit transactions

**URLs**:
- `/accounts/skill-swap/` - Browse all skill swaps
- `/accounts/skill-swap/create/` - Create listing
- `/accounts/skill-swap/<id>/` - View listing
- `/accounts/skill-swap/<id>/edit/` - Edit listing
- `/accounts/credits/` - View credit transactions
- `/accounts/credits/create/` - Record a swap

### 3. Profile Mode Management

**Purpose**: Unified dashboard to manage all modes

**Features**:
- View all active modes
- Toggle mode activation on/off
- Switch active mode for UI context
- Quick links to manage each mode
- Credit balance display

**URLs**:
- `/accounts/modes/` - Mode dashboard
- `/accounts/modes/toggle/` - Toggle mode (POST)
- `/accounts/modes/set-active/` - Set active mode (POST)

---

## Database Models

### Skill
Reusable skills model used by both Freelance and Skill Swap modes.

**Fields**:
- `name` - Skill name (unique)
- `slug` - URL-friendly slug
- `category` - Category (design, development, marketing, etc.)
- `description` - Optional description
- `icon` - Icon class or emoji
- `is_active` - Active status

### FreelanceListing
Freelance mode listing.

**Fields**:
- `user` - OneToOne to User
- `title` - Professional title
- `bio` - Professional bio
- `headline` - Short headline
- `skills` - ManyToMany to Skill
- `expertise_tags` - Comma-separated tags
- `pricing_type` - hourly/project/both
- `hourly_rate` - Hourly rate in USD
- `project_rate_min/max` - Project rate range
- `currency` - Currency code (default: USD)
- `portfolio_url`, `github_url`, `linkedin_url`, `behance_url` - Portfolio links
- `availability_status` - available/busy/unavailable
- `availability_notes` - Additional notes
- `timezone` - Timezone
- `is_active`, `is_featured`, `is_verified` - Status flags

### FreelancePortfolioItem
Portfolio items for freelance listings.

**Fields**:
- `listing` - ForeignKey to FreelanceListing
- `item_type` - image/link/case_study
- `title`, `description` - Item details
- `image` - Image upload
- `url` - Link URL
- `case_study_content` - Case study content (markdown)
- `order` - Display order
- `is_featured` - Featured flag

### SkillSwapListing
Skill swap mode listing.

**Fields**:
- `user` - OneToOne to User
- `bio` - Swap-specific bio
- `skills_offered` - ManyToMany to Skill
- `skills_wanted` - ManyToMany to Skill
- `additional_skills_offered/wanted` - Text fields
- `credits_earned` - Total credits earned
- `credits_spent` - Total credits spent
- `location_preference` - Location preference
- `accepts_remote` - Remote swaps flag
- `is_active`, `is_verified` - Status flags

**Properties**:
- `credits_balance` - Calculated balance (earned - spent)

### SkillCredit
Credit transaction for skill swaps.

**Fields**:
- `from_user` - User who provided service
- `to_user` - User who received service
- `transaction_type` - earned/spent
- `credits` - Number of credits (hours)
- `skill_swapped` - ForeignKey to Skill
- `description` - Swap description
- `swap_date` - Date of swap
- `status` - pending/approved/rejected
- `verified_by` - User who verified
- `verified_at` - Verification timestamp
- `notes` - Additional notes

**Auto-updates**: When approved, automatically updates both users' credit totals.

### CustomUser Extensions

**New Fields**:
- `is_freelancer_active` - Freelance mode active flag
- `is_skill_swap_active` - Skill swap mode active flag
- `active_mode` - Currently active mode for UI context

**New Properties**:
- `has_freelance_listing` - Check if user has freelance listing
- `has_skill_swap_listing` - Check if user has skill swap listing
- `active_modes` - List of active modes
- `total_skill_credits` - Total credits earned

---

## User Flow

### Creating a Freelance Listing

1. User navigates to `/accounts/modes/`
2. Clicks "Set Up" on Freelance card
3. Fills out freelance form:
   - Basic info (title, bio, headline)
   - Skills selection
   - Pricing (hourly/project rates)
   - Portfolio links
   - Availability
4. Saves → Listing created, freelance mode auto-activated
5. Can add portfolio items via "Manage Portfolio"

### Creating a Skill Swap Listing

1. User navigates to `/accounts/modes/`
2. Clicks "Set Up" on Skill Swap card
3. Fills out skill swap form:
   - Bio
   - Skills offered (select from Skill model + text)
   - Skills wanted (select from Skill model + text)
   - Location preferences
4. Saves → Listing created, skill swap mode auto-activated

### Recording a Skill Swap

1. User navigates to `/accounts/credits/create/`
2. Selects swap partner
3. Chooses transaction type (earned/spent)
4. Enters credits (hours)
5. Selects skill swapped
6. Enters description and date
7. Submits → Transaction created as "pending"
8. Swap partner approves → Credits updated automatically

### Switching Modes

1. User navigates to `/accounts/modes/`
2. Uses toggle buttons to activate/deactivate modes
3. Uses dropdown to set active mode for UI context
4. Navigation and profile context update based on active mode

---

## Admin Interface

All new models are registered in Django admin:

- **Skill** - Manage skills catalog
- **FreelanceListing** - Manage freelance listings with inline portfolio items
- **FreelancePortfolioItem** - Manage portfolio items
- **SkillSwapListing** - Manage skill swap listings
- **SkillCredit** - Manage credit transactions with bulk approve/reject actions

**Admin Features**:
- Filter by status, category, location
- Search by user, skills, description
- Bulk actions for credits (approve/reject)
- Inline editing for portfolio items

---

## Integration with Existing Features

### Service Provider Mode
- Fully integrated and unchanged
- Users can have provider profile + freelance + skill swap simultaneously
- All modes appear in mode dashboard

### Navigation
- "Profile Modes" link added to user dropdown menu
- Mode dashboard accessible from navigation
- Active mode affects UI context (can be extended)

### User Dashboard
- Can be extended to show mode-specific content based on `active_mode`
- Links to mode dashboard available

---

## API Considerations

The system is designed to be API-ready. Future API endpoints could include:

```
GET    /api/freelance/              # List freelance listings
GET    /api/freelance/<id>/         # Freelance detail
GET    /api/skill-swap/             # List skill swap listings
GET    /api/skill-swap/<id>/        # Skill swap detail
GET    /api/skills/                 # List skills
POST   /api/credits/                # Create credit transaction
GET    /api/credits/                # List user's credits
```

---

## Migration Notes

Run the migration to add all new models:

```bash
python manage.py migrate accounts
```

This will:
- Add mode fields to CustomUser
- Create Skill model
- Create FreelanceListing and FreelancePortfolioItem models
- Create SkillSwapListing and SkillCredit models
- Set up all relationships

---

## Future Enhancements

Potential future features:
- Availability calendar for freelancers
- Project proposal/bidding system
- Skill matching algorithm for skill swaps
- Credit marketplace (buy/sell credits)
- Mode-specific search filters
- API endpoints for all modes
- Mobile app integration

---

## Testing Checklist

- [ ] Create freelance listing
- [ ] Create skill swap listing
- [ ] Toggle modes on/off
- [ ] Switch active mode
- [ ] Add portfolio items
- [ ] Record credit transaction
- [ ] Approve credit transaction
- [ ] Browse freelance listings
- [ ] Browse skill swap listings
- [ ] Admin interface for all models
- [ ] Multiple modes active simultaneously
- [ ] Integration with existing provider profile

---

## Notes

- Users can activate multiple modes simultaneously
- Each mode has its own listing/profile
- Mode activation is independent of listing creation
- Credits are automatically calculated when transactions are approved
- All modes integrate seamlessly with existing provider functionality
