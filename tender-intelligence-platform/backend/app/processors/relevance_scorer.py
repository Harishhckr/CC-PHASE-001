"""
Relevance scorer for calculating tender relevance scores
"""
from typing import List, Optional
from datetime import datetime, timedelta
from loguru import logger
from app.config import MDM_KEYWORDS


class RelevanceScorer:
    """Calculate relevance scores for tenders"""

    def __init__(self):
        self.keywords = MDM_KEYWORDS

    def calculate_score(
        self,
        matched_keywords: List[str],
        tender_value: Optional[float] = None,
        end_date: Optional[datetime] = None,
        location: Optional[str] = None,
        preferred_locations: List[str] = None
    ) -> float:
        """
        Calculate overall relevance score (0-100)

        Scoring components:
        - Keyword match score: 60% (based on keyword priorities and count)
        - Value score: 20% (higher value = higher score)
        - Recency score: 15% (newer/longer duration = higher score)
        - Location score: 5% (preferred location boost)

        Args:
            matched_keywords: List of matched keywords
            tender_value: Tender value in INR
            end_date: Tender end date
            location: Tender location
            preferred_locations: List of preferred locations

        Returns:
            Relevance score (0-100)
        """
        if not matched_keywords:
            return 0.0

        try:
            # 1. Keyword Score (60 points)
            keyword_score = self._calculate_keyword_score(matched_keywords)

            # 2. Value Score (20 points)
            value_score = self._calculate_value_score(tender_value)

            # 3. Recency/Duration Score (15 points)
            recency_score = self._calculate_recency_score(end_date)

            # 4. Location Score (5 points)
            location_score = self._calculate_location_score(location, preferred_locations)

            # Total score
            total_score = keyword_score + value_score + recency_score + location_score

            # Ensure score is within 0-100 range
            return min(max(total_score, 0.0), 100.0)

        except Exception as e:
            logger.error(f"Error calculating relevance score: {e}")
            return 0.0

    def _calculate_keyword_score(self, matched_keywords: List[str]) -> float:
        """
        Calculate score based on matched keywords

        - Base score from keyword priorities
        - Bonus for multiple keyword matches
        - Maximum 60 points
        """
        if not matched_keywords:
            return 0.0

        # Sum of keyword priorities
        priority_sum = sum(self.keywords.get(kw, 5) for kw in matched_keywords)

        # Average priority
        avg_priority = priority_sum / len(matched_keywords)

        # Base score from average priority (0-10 priority maps to 0-40 points)
        base_score = (avg_priority / 10) * 40

        # Bonus for multiple matches (up to 20 points)
        match_count_bonus = min(len(matched_keywords) * 3, 20)

        return min(base_score + match_count_bonus, 60.0)

    def _calculate_value_score(self, tender_value: Optional[float]) -> float:
        """
        Calculate score based on tender value

        - Higher value = higher score
        - Maximum 20 points
        """
        if not tender_value or tender_value <= 0:
            return 5.0  # Base score for unknown value

        # Logarithmic scale for value scoring
        # ₹1 Lakh = 5 points, ₹1 Crore = 15 points, ₹10 Crore+ = 20 points
        if tender_value >= 100000000:  # ₹10 Crore+
            return 20.0
        elif tender_value >= 10000000:  # ₹1 Crore+
            return 15.0
        elif tender_value >= 1000000:  # ₹10 Lakh+
            return 12.0
        elif tender_value >= 100000:  # ₹1 Lakh+
            return 8.0
        else:
            return 5.0

    def _calculate_recency_score(self, end_date: Optional[datetime]) -> float:
        """
        Calculate score based on tender recency and duration

        - Newer tenders with more time remaining = higher score
        - Maximum 15 points
        """
        if not end_date:
            return 5.0  # Base score for unknown date

        now = datetime.now()

        # Already expired
        if end_date < now:
            return 0.0

        # Calculate days remaining
        days_remaining = (end_date - now).days

        # Score based on days remaining
        if days_remaining >= 30:  # 30+ days
            return 15.0
        elif days_remaining >= 14:  # 14-30 days
            return 12.0
        elif days_remaining >= 7:  # 7-14 days
            return 10.0
        elif days_remaining >= 3:  # 3-7 days
            return 7.0
        elif days_remaining >= 1:  # 1-3 days
            return 5.0
        else:  # Less than 1 day
            return 3.0

    def _calculate_location_score(
        self,
        location: Optional[str],
        preferred_locations: Optional[List[str]] = None
    ) -> float:
        """
        Calculate score based on location match

        - Preferred location = bonus points
        - Maximum 5 points
        """
        if not location:
            return 2.0  # Base score for unknown location

        if not preferred_locations:
            return 2.0

        location_lower = location.lower()

        # Check if location matches any preferred location
        for pref_loc in preferred_locations:
            if pref_loc.lower() in location_lower:
                return 5.0

        return 2.0

    def get_score_breakdown(
        self,
        matched_keywords: List[str],
        tender_value: Optional[float] = None,
        end_date: Optional[datetime] = None,
        location: Optional[str] = None,
        preferred_locations: List[str] = None
    ) -> dict:
        """
        Get detailed score breakdown

        Returns:
            Dictionary with score components
        """
        return {
            "keyword_score": self._calculate_keyword_score(matched_keywords),
            "value_score": self._calculate_value_score(tender_value),
            "recency_score": self._calculate_recency_score(end_date),
            "location_score": self._calculate_location_score(location, preferred_locations),
            "total_score": self.calculate_score(
                matched_keywords, tender_value, end_date, location, preferred_locations
            )
        }
