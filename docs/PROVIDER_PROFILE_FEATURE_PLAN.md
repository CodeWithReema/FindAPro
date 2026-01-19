# Provider Profile Creation Feature - Implementation Plan

## Overview
Comprehensive feature allowing users to join as professionals and build business profiles with all requested capabilities.

---

## 1. Registration Flow (Option C - Both)

### 1.1 During Registration
- **Modify `RegisterView`** in `apps/accounts/views.py`:
  - If `user_type='provider'` selected → redirect to provider profile creation
  - If `user_type='customer'` → normal redirect to home
  - Store registration context in session if needed

### 1.2 "Join as Pro" for Existing Users
- **New View**: `JoinAsProView` in `apps/providers/views.py`
- **URL**: `/providers/join/`
- **Access**: Available to any authenticated user without a provider profile
- **Button/Link**: Add to navigation menu, dashboard, or home page
- **Logic**: Check if user already has `provider_profile`, if yes → redirect to edit

---

## 2. Profile Creation Process

### 2.1 Multi-Step Form Structure
**5 Steps with Progress Indicator:**

1. **Step 1: Basic Information**
   - Business name (required)
   - Category selection (required)
   - Tagline (optional)
   - Description (required)
   - Skills (comma-separated, required)

2. **Step 2: Contact & Location**
   - Email (pre-fill from user account, editable)
   - Phone (required)
   - Website (optional)
   - Address (optional)
   - City (required)
   - State (required)
   - ZIP Code (required)

3. **Step 3: Business Details**
   - Pricing range (required)
   - Years of experience (required)
   - Service areas/coverage zones (new field - see below)
   - Business hours/availability schedule (new model - see below)

4. **Step 4: Media & Portfolio**
   - Logo upload (optional)
   - Main image upload (optional)
   - Gallery/portfolio images (multiple, optional)
   - Image captions and alt text

5. **Step 5: Availability & Emergency**
   - Accept emergency requests? (checkbox)
   - Emergency rate info (if yes)
   - Currently available? (checkbox)
   - Additional availability notes

### 2.2 Draft Mode
- **New Field**: `is_draft` (BooleanField) on ServiceProvider model
- **Behavior**: 
  - Users can save progress at any step
  - Draft profiles are NOT visible in search/listing
  - Users can return to complete later
  - Progress saved in session or database
- **"Save & Continue Later"** button on each step

### 2.3 Progress Indicator
- Visual progress bar showing: "Step X of 5"
- Percentage complete
- Required fields highlighted
- Completion status per step

---

## 3. Database Models - New Fields & Models

### 3.1 ServiceProvider Model Extensions
```python
# Add to existing ServiceProvider model:
- is_draft = BooleanField(default=True)  # Draft mode
- service_areas = TextField(blank=True)  # Coverage zones (e.g., "Within 25 miles of City, State")
- submitted_for_review_at = DateTimeField(null=True, blank=True)  # When submitted for approval
- approved_at = DateTimeField(null=True, blank=True)  # When approved by admin
- rejection_reason = TextField(blank=True)  # If rejected
```

### 3.2 New Models

#### BusinessHours Model
```python
class BusinessHours(models.Model):
    provider = models.OneToOneField(ServiceProvider, on_delete=models.CASCADE, related_name='business_hours')
    
    # Monday through Sunday
    monday_open = models.TimeField(null=True, blank=True)
    monday_close = models.TimeField(null=True, blank=True)
    monday_closed = models.BooleanField(default=False)
    
    # Repeat for tuesday, wednesday, thursday, friday, saturday, sunday
    
    # Or use JSONField for flexibility:
    hours_schedule = models.JSONField(default=dict)  # More flexible approach
    
    # Alternative: Use a separate model for each day
    # BusinessHoursDay model with day_of_week, open_time, close_time, is_closed
```

#### ServiceArea Model (Alternative to TextField)
```python
class ServiceArea(models.Model):
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='service_areas')
    zip_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    radius_miles = models.PositiveIntegerField(default=25, help_text='Service radius in miles')
    is_primary = models.BooleanField(default=False)  # Primary service location
```

#### Certification Model
```python
class ProviderCertification(models.Model):
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField(max_length=200)  # e.g., "Licensed Electrician"
    issuing_organization = models.CharField(max_length=200, blank=True)
    license_number = models.CharField(max_length=100, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    verification_document = models.FileField(upload_to='certifications/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)  # Admin verified
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## 4. Verification & Approval System

### 4.1 Email Verification
- Send verification email when profile is submitted
- Link in email verifies email address
- `email_verified` field on ServiceProvider

### 4.2 Phone Verification (Optional)
- SMS verification code
- `phone_verified` field on ServiceProvider
- Integration with Twilio or similar (optional, can be added later)

### 4.3 Admin Approval Workflow
- **Status Choices**:
  - `draft` - Not submitted
  - `pending_review` - Submitted, awaiting admin approval
  - `approved` - Approved and active
  - `rejected` - Rejected (with reason)
  - `suspended` - Temporarily suspended

- **New Field**: `approval_status` (CharField with choices)
- **Admin Actions**:
  - Approve profile → sets `is_active=True`, `is_draft=False`, `approval_status='approved'`
  - Reject profile → sets `approval_status='rejected'`, sends email with reason
  - Request changes → sends notification to provider

### 4.4 Admin Notifications
- Email admin when new profile submitted
- Admin dashboard shows pending reviews
- Bulk approve/reject actions

---

## 5. Access Control & User Experience

### 5.1 Profile Switching
- Users can have both customer and provider accounts
- **Dashboard Toggle**: Switch between "Customer View" and "Provider View"
- Context-aware navigation based on current view mode
- Store preference in session or user settings

### 5.2 One Profile Per User
- Enforce OneToOne relationship (already exists)
- If user tries to create second profile → redirect to edit existing
- Clear messaging: "You already have a provider profile"

### 5.3 Profile Completion
- **Completion Score**: Calculate based on filled fields
- **Required Fields** (minimum to submit):
  - Business name
  - Category
  - Description
  - Skills
  - Phone
  - City, State, ZIP
  - Pricing range
  - Years of experience

- **Optional but Recommended**:
  - Logo/image
  - Website
  - Business hours
  - Service areas
  - Certifications

---

## 6. Forms & Views

### 6.1 Multi-Step Form Class
```python
class ProviderProfileMultiStepForm:
    # Use formset or wizard pattern
    # Step 1: BasicInfoForm
    # Step 2: ContactLocationForm
    # Step 3: BusinessDetailsForm
    # Step 4: MediaForm (with image uploads)
    # Step 5: AvailabilityForm
```

### 6.2 Views Needed
1. **ProviderProfileCreateView** - Main multi-step creation
2. **ProviderProfileEditView** - Edit existing profile
3. **ProviderProfilePreviewView** - Preview before submission
4. **ProviderProfileStatusView** - View approval status
5. **JoinAsProView** - Entry point for existing users

### 6.3 URL Patterns
```python
path('join/', views.JoinAsProView.as_view(), name='join_as_pro'),
path('profile/create/', views.ProviderProfileCreateView.as_view(), name='profile_create'),
path('profile/edit/', views.ProviderProfileEditView.as_view(), name='profile_edit'),
path('profile/preview/', views.ProviderProfilePreviewView.as_view(), name='profile_preview'),
path('profile/status/', views.ProviderProfileStatusView.as_view(), name='profile_status'),
```

---

## 7. Templates

### 7.1 Templates to Create
- `providers/join_as_pro.html` - Landing page for joining
- `providers/profile/create.html` - Multi-step form container
- `providers/profile/step1_basic.html` - Step 1 form
- `providers/profile/step2_contact.html` - Step 2 form
- `providers/profile/step3_business.html` - Step 3 form
- `providers/profile/step4_media.html` - Step 4 form
- `providers/profile/step5_availability.html` - Step 5 form
- `providers/profile/preview.html` - Preview before submission
- `providers/profile/status.html` - Approval status page
- `providers/profile/edit.html` - Edit existing profile

### 7.2 UI Components
- Progress indicator component
- Step navigation (Previous/Next buttons)
- Save draft button
- Field validation indicators
- Image upload with preview
- Business hours picker widget

---

## 8. Additional Features

### 8.1 Portfolio/Gallery Upload
- **Already exists**: `ProviderImage` model
- **Enhancement**: Allow bulk upload during profile creation
- Drag-and-drop interface
- Image reordering
- Set featured image

### 8.2 Service Areas/Coverage Zones
- **Option 1**: Simple text field ("Within 25 miles of City, State")
- **Option 2**: Multiple ServiceArea entries (more structured)
- **Option 3**: ZIP code list with radius
- **Recommendation**: Start with Option 1, can enhance later

### 8.3 Business Hours/Availability Schedule
- **Model**: BusinessHours (see section 3.2)
- **UI**: Weekly schedule picker
- **Features**:
  - Set hours for each day
  - Mark days as closed
  - Different hours for different days
  - "Available 24/7" option
  - Holiday/exception handling (future)

### 8.4 Certifications/Licenses
- **Model**: ProviderCertification (see section 3.2)
- **Features**:
  - Add multiple certifications
  - Upload verification documents
  - Expiry date tracking
  - Admin verification
  - Display badges on profile

---

## 9. Implementation Phases

### Phase 1: Core Profile Creation (MVP)
- [ ] Multi-step form (5 steps)
- [ ] Basic fields (existing ServiceProvider fields)
- [ ] Draft mode
- [ ] Progress indicator
- [ ] Registration flow integration
- [ ] "Join as Pro" for existing users
- [ ] Basic validation

### Phase 2: Media & Portfolio
- [ ] Logo upload
- [ ] Main image upload
- [ ] Gallery/portfolio upload (enhance existing)
- [ ] Image management (reorder, delete, featured)

### Phase 3: Business Details
- [ ] Business hours model & form
- [ ] Service areas field/model
- [ ] Certifications model & form
- [ ] Enhanced business details step

### Phase 4: Verification & Approval
- [ ] Email verification
- [ ] Admin approval workflow
- [ ] Status tracking
- [ ] Admin notifications
- [ ] Rejection with reason

### Phase 5: Polish & Enhancements
- [ ] Profile completion score
- [ ] Preview before submission
- [ ] Edit existing profile
- [ ] Profile status dashboard
- [ ] User switching (customer/provider view)
- [ ] Phone verification (optional)

---

## 10. Technical Considerations

### 10.1 Form Handling
- Use Django FormWizard or custom session-based approach
- Store form data in session between steps
- Handle back navigation
- Validate on each step
- Final validation before submission

### 10.2 File Uploads
- Use Django's FileField/ImageField
- Configure MEDIA_ROOT and MEDIA_URL
- Image validation (size, format)
- Thumbnail generation (optional)
- Progress indicators for uploads

### 10.3 Slug Generation
- Auto-generate slug from business name
- Handle duplicates (append number)
- Allow manual override (optional)

### 10.4 Permissions
- Only profile owner can edit
- Admin can edit/approve/reject
- Draft profiles hidden from public
- Pending profiles hidden until approved

### 10.5 Notifications
- Email on profile submission
- Email on approval/rejection
- Email on status changes
- In-app notifications (optional)

---

## 11. Questions for Discussion

1. **Business Hours**: Simple weekly schedule or more complex (holidays, exceptions)?
2. **Service Areas**: Text field or structured model with ZIP codes?
3. **Certifications**: Required or optional? Admin verification required?
4. **Approval**: Auto-approve after email verification, or always require admin?
5. **Phone Verification**: Implement now or later?
6. **Profile Completeness**: Show completion percentage? Require minimum % to submit?
7. **Multiple Categories**: Can a provider belong to multiple categories? (Currently one-to-one)
8. **Pricing**: Show pricing range only, or allow custom pricing fields?

---

## 12. Next Steps

1. Review and approve this plan
2. Answer discussion questions
3. Prioritize phases
4. Start implementation with Phase 1
5. Iterate based on feedback

---

## Notes

- All existing functionality should remain intact
- Backward compatible with existing provider profiles
- Consider migration strategy for existing data
- Test thoroughly with various user scenarios
- Ensure mobile-responsive design
