"""
Smart matching algorithm service for skill swaps and collaborations.
"""

from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta

from .models import CustomUser
from .modes_models import SkillSwapListing, FreelanceListing, Skill
from .matching_models import Match, MatchHistory


class MatchingService:
    """Service class for calculating matches between users."""
    
    def __init__(self, user):
        self.user = user
    
    def find_skill_swap_matches(self, limit=10, min_score=30):
        """
        Find skill swap matches for the user.
        
        Returns list of Match objects sorted by compatibility score.
        """
        if not hasattr(self.user, 'skill_swap_listing') or not self.user.skill_swap_listing.is_active:
            return []
        
        user_listing = self.user.skill_swap_listing
        
        # Get users with active skill swap listings (excluding self)
        potential_matches = CustomUser.objects.filter(
            is_skill_swap_active=True,
            skill_swap_listing__is_active=True
        ).exclude(id=self.user.id).select_related('skill_swap_listing')
        
        # Exclude users already matched or marked as not interested
        excluded_users = self._get_excluded_users('skill_swap')
        potential_matches = potential_matches.exclude(id__in=excluded_users)
        
        matches = []
        for other_user in potential_matches:
            match_score = self._calculate_skill_swap_score(user_listing, other_user.skill_swap_listing)
            
            if match_score['compatibility_score'] >= min_score:
                match = self._create_or_update_match(
                    user_a=self.user,
                    user_b=other_user,
                    match_type='skill_swap',
                    score_data=match_score
                )
                matches.append(match)
        
        # Sort by compatibility score
        matches.sort(key=lambda x: x.compatibility_score, reverse=True)
        return matches[:limit]
    
    def find_freelance_collab_matches(self, limit=10, min_score=30):
        """
        Find freelance collaboration matches for the user.
        
        Returns list of Match objects sorted by compatibility score.
        """
        if not hasattr(self.user, 'freelance_listing') or not self.user.freelance_listing.is_active:
            return []
        
        user_listing = self.user.freelance_listing
        
        # Get users with active freelance listings (excluding self)
        potential_matches = CustomUser.objects.filter(
            is_freelancer_active=True,
            freelance_listing__is_active=True
        ).exclude(id=self.user.id).select_related('freelance_listing')
        
        # Exclude users already matched or marked as not interested
        excluded_users = self._get_excluded_users('freelance_collab')
        potential_matches = potential_matches.exclude(id__in=excluded_users)
        
        matches = []
        for other_user in potential_matches:
            match_score = self._calculate_freelance_score(user_listing, other_user.freelance_listing)
            
            if match_score['compatibility_score'] >= min_score:
                match = self._create_or_update_match(
                    user_a=self.user,
                    user_b=other_user,
                    match_type='freelance_collab',
                    score_data=match_score
                )
                matches.append(match)
        
        # Sort by compatibility score
        matches.sort(key=lambda x: x.compatibility_score, reverse=True)
        return matches[:limit]
    
    def _calculate_skill_swap_score(self, listing_a, listing_b):
        """
        Calculate compatibility score for skill swap match.
        
        Returns dict with score breakdown.
        """
        score_data = {
            'skill_overlap_percentage': 0,
            'matching_skills': [],
            'geographic_proximity_score': 0,
            'reputation_score': 0,
            'availability_score': 0,
            'compatibility_score': 0,
        }
        
        # 1. Skill Overlap (40% weight)
        # Convert to sets of strings for comparison (handles both Skill objects and strings)
        def normalize_skill(skill):
            """Convert skill to string, handling both Skill objects and strings."""
            if hasattr(skill, 'name'):
                return skill.name.lower().strip()
            return str(skill).lower().strip()
        
        skills_a_offered = set(normalize_skill(s) for s in listing_a.skills_offered_list)
        skills_b_wanted = set(normalize_skill(s) for s in listing_b.skills_wanted_list)
        
        skills_b_offered = set(normalize_skill(s) for s in listing_b.skills_offered_list)
        skills_a_wanted = set(normalize_skill(s) for s in listing_a.skills_wanted_list)
        
        # Find matching skills (A offers what B wants, B offers what A wants)
        matches_ab = skills_a_offered.intersection(skills_b_wanted)
        matches_ba = skills_b_offered.intersection(skills_a_wanted)
        all_matches = matches_ab.union(matches_ba)
        
        total_skills = len(skills_a_offered) + len(skills_a_wanted) + len(skills_b_offered) + len(skills_b_wanted)
        if total_skills > 0:
            score_data['skill_overlap_percentage'] = (len(all_matches) / total_skills) * 100
        else:
            score_data['skill_overlap_percentage'] = 0
        
        # Convert back to readable skill names (capitalize first letter)
        score_data['matching_skills'] = [s.capitalize() for s in list(all_matches)[:10]]
        
        skill_score = min(score_data['skill_overlap_percentage'] * 2, 40)  # Max 40 points
        
        # 2. Geographic Proximity (20% weight)
        proximity_score = self._calculate_proximity_score(listing_a.user, listing_b.user)
        score_data['geographic_proximity_score'] = proximity_score * 20
        
        # 3. Reputation Score (20% weight)
        reputation_score = self._calculate_reputation_score(listing_a.user, listing_b.user)
        score_data['reputation_score'] = reputation_score * 20
        
        # 4. Availability Score (20% weight)
        # For skill swaps, check if both accept remote or are in same location
        availability_score = 0
        if listing_a.accepts_remote and listing_b.accepts_remote:
            availability_score = 20
        elif listing_a.location_preference and listing_b.location_preference:
            # Simple location matching
            if listing_a.location_preference.lower() == listing_b.location_preference.lower():
                availability_score = 20
            elif 'remote' in listing_a.location_preference.lower() or 'remote' in listing_b.location_preference.lower():
                availability_score = 15
        else:
            availability_score = 10  # Default score
        
        score_data['availability_score'] = availability_score
        
        # Calculate total compatibility score
        total_score = skill_score + score_data['geographic_proximity_score'] + score_data['reputation_score'] + availability_score
        score_data['compatibility_score'] = min(total_score, 100)
        
        return score_data
    
    def _calculate_freelance_score(self, listing_a, listing_b):
        """
        Calculate compatibility score for freelance collaboration match.
        
        Returns dict with score breakdown.
        """
        score_data = {
            'skill_overlap_percentage': 0,
            'matching_skills': [],
            'geographic_proximity_score': 0,
            'reputation_score': 0,
            'availability_score': 0,
            'compatibility_score': 0,
        }
        
        # 1. Skill Overlap (50% weight)
        skills_a = set(listing_a.skills.all())
        skills_b = set(listing_b.skills.all())
        
        matching_skills = skills_a.intersection(skills_b)
        total_unique_skills = len(skills_a.union(skills_b))
        
        if total_unique_skills > 0:
            score_data['skill_overlap_percentage'] = (len(matching_skills) / total_unique_skills) * 100
        else:
            score_data['skill_overlap_percentage'] = 0
        
        score_data['matching_skills'] = [str(skill.name) for skill in matching_skills[:10]]
        
        skill_score = min(score_data['skill_overlap_percentage'] * 0.5, 50)  # Max 50 points
        
        # 2. Geographic Proximity (20% weight)
        proximity_score = self._calculate_proximity_score(listing_a.user, listing_b.user)
        score_data['geographic_proximity_score'] = proximity_score * 20
        
        # 3. Reputation Score (20% weight)
        reputation_score = self._calculate_reputation_score(listing_a.user, listing_b.user)
        score_data['reputation_score'] = reputation_score * 20
        
        # 4. Availability Score (10% weight)
        # Check if both are available
        availability_score = 0
        if listing_a.availability_status == 'available' and listing_b.availability_status == 'available':
            availability_score = 10
        elif listing_a.availability_status == 'busy' or listing_b.availability_status == 'busy':
            availability_score = 5
        else:
            availability_score = 2
        
        score_data['availability_score'] = availability_score
        
        # Calculate total compatibility score
        total_score = skill_score + score_data['geographic_proximity_score'] + score_data['reputation_score'] + availability_score
        score_data['compatibility_score'] = min(total_score, 100)
        
        return score_data
    
    def _calculate_proximity_score(self, user_a, user_b):
        """
        Calculate geographic proximity score (0-1).
        
        Returns score based on location similarity.
        """
        # Simple proximity based on city/state/zip
        if not user_a.city or not user_b.city:
            return 0.5  # Default if no location data
        
        # Same city = 1.0
        if user_a.city.lower() == user_b.city.lower() and user_a.state.lower() == user_b.state.lower():
            return 1.0
        
        # Same state = 0.7
        if user_a.state.lower() == user_b.state.lower():
            return 0.7
        
        # Same zip code prefix (first 3 digits) = 0.8
        if user_a.zip_code and user_b.zip_code:
            if user_a.zip_code[:3] == user_b.zip_code[:3]:
                return 0.8
        
        # Different states = 0.3
        return 0.3
    
    def _calculate_reputation_score(self, user_a, user_b):
        """
        Calculate combined reputation score (0-1).
        
        Based on ratings, reviews, verification status.
        """
        score = 0.5  # Base score
        
        # Check provider profiles for ratings
        if hasattr(user_a, 'provider_profile') and user_a.provider_profile.is_active:
            rating_a = user_a.provider_profile.average_rating
            reviews_a = user_a.provider_profile.review_count
            if rating_a:
                score += (rating_a - 3) * 0.1  # Boost for ratings above 3
            if reviews_a >= 10:
                score += 0.1
            if user_a.provider_profile.is_verified:
                score += 0.1
        
        if hasattr(user_b, 'provider_profile') and user_b.provider_profile.is_active:
            rating_b = user_b.provider_profile.average_rating
            reviews_b = user_b.provider_profile.review_count
            if rating_b:
                score += (rating_b - 3) * 0.1
            if reviews_b >= 10:
                score += 0.1
            if user_b.provider_profile.is_verified:
                score += 0.1
        
        # Check freelance/swap verification
        if hasattr(user_a, 'freelance_listing') and user_a.freelance_listing.is_verified:
            score += 0.05
        if hasattr(user_b, 'freelance_listing') and user_b.freelance_listing.is_verified:
            score += 0.05
        if hasattr(user_a, 'skill_swap_listing') and user_a.skill_swap_listing.is_verified:
            score += 0.05
        if hasattr(user_b, 'skill_swap_listing') and user_b.skill_swap_listing.is_verified:
            score += 0.05
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _get_excluded_users(self, match_type):
        """Get list of user IDs to exclude from matching."""
        excluded = set()
        
        # Users marked as not interested
        not_interested_matches = Match.objects.filter(
            Q(user_a=self.user) | Q(user_b=self.user),
            match_type=match_type,
            status='not_interested'
        )
        for match in not_interested_matches:
            if match.user_a == self.user:
                excluded.add(match.user_b.id)
            else:
                excluded.add(match.user_a.id)
        
        # Users already connected
        connected_matches = Match.objects.filter(
            Q(user_a=self.user) | Q(user_b=self.user),
            match_type=match_type,
            status='connected'
        )
        for match in connected_matches:
            if match.user_a == self.user:
                excluded.add(match.user_b.id)
            else:
                excluded.add(match.user_a.id)
        
        return excluded
    
    def _create_or_update_match(self, user_a, user_b, match_type, score_data):
        """Create or update a Match record."""
        # Ensure consistent ordering (lower ID first)
        if user_a.id > user_b.id:
            user_a, user_b = user_b, user_a
        
        match, created = Match.objects.get_or_create(
            user_a=user_a,
            user_b=user_b,
            match_type=match_type,
            defaults={
                'compatibility_score': score_data['compatibility_score'],
                'skill_overlap_percentage': score_data['skill_overlap_percentage'],
                'matching_skills': score_data['matching_skills'],
                'geographic_proximity_score': score_data['geographic_proximity_score'],
                'reputation_score': score_data['reputation_score'],
                'availability_score': score_data['availability_score'],
                'status': 'pending',
            }
        )
        
        if not created and match.status != 'not_interested':
            # Update existing match with new scores (unless marked as not interested)
            match.compatibility_score = score_data['compatibility_score']
            match.skill_overlap_percentage = score_data['skill_overlap_percentage']
            match.matching_skills = score_data['matching_skills']
            match.geographic_proximity_score = score_data['geographic_proximity_score']
            match.reputation_score = score_data['reputation_score']
            match.availability_score = score_data['availability_score']
            match.save()
        
        # Record in history
        MatchHistory.objects.get_or_create(
            user=self.user,
            matched_user=user_b if self.user == user_a else user_a,
            action='suggested',
            defaults={'match': match}
        )
        
        return match
    
    def get_all_matches(self, match_type=None, limit=10):
        """Get all matches for the user, optionally filtered by type."""
        matches = Match.objects.filter(
            Q(user_a=self.user) | Q(user_b=self.user)
        ).exclude(status='not_interested')
        
        if match_type:
            matches = matches.filter(match_type=match_type)
        
        return matches.select_related('user_a', 'user_b').order_by('-compatibility_score')[:limit]
    
    def get_new_matches_count(self, days=7):
        """Get count of new matches in the last N days."""
        cutoff_date = timezone.now() - timedelta(days=days)
        return Match.objects.filter(
            Q(user_a=self.user) | Q(user_b=self.user),
            created_at__gte=cutoff_date,
            status__in=['pending', 'viewed']
        ).count()
