"""
Keyword filter for matching MDM keywords in tender text
"""
import re
from typing import List, Dict
from fuzzywuzzy import fuzz
from loguru import logger
from app.config import MDM_KEYWORDS


class KeywordFilter:
    """Keyword matching and filtering"""

    def __init__(self, keywords: Dict[str, int] = None, fuzzy_threshold: int = 85):
        """
        Initialize keyword filter

        Args:
            keywords: Dictionary of keywords and their priorities
            fuzzy_threshold: Minimum fuzzy match score (0-100)
        """
        self.keywords = keywords or MDM_KEYWORDS
        self.fuzzy_threshold = fuzzy_threshold

    def match_keywords(self, text: str) -> List[str]:
        """
        Match keywords in text

        Args:
            text: Text to search for keywords

        Returns:
            List of matched keywords
        """
        if not text:
            return []

        text_lower = text.lower()
        matched = []

        for keyword in self.keywords.keys():
            # Exact match
            if keyword.lower() in text_lower:
                matched.append(keyword)
                continue

            # Fuzzy match for compound keywords
            if self._fuzzy_match(keyword, text_lower):
                matched.append(keyword)

        return list(set(matched))  # Remove duplicates

    def _fuzzy_match(self, keyword: str, text: str) -> bool:
        """
        Perform fuzzy matching for keywords

        Args:
            keyword: Keyword to match
            text: Text to search in

        Returns:
            True if fuzzy match found
        """
        # Split text into chunks for fuzzy matching
        words = text.split()
        keyword_words = keyword.split()

        # For single-word keywords, check against text words
        if len(keyword_words) == 1:
            for word in words:
                if fuzz.ratio(keyword.lower(), word.lower()) >= self.fuzzy_threshold:
                    return True
            return False

        # For multi-word keywords, use sliding window
        keyword_len = len(keyword_words)
        for i in range(len(words) - keyword_len + 1):
            chunk = " ".join(words[i:i + keyword_len])
            if fuzz.ratio(keyword.lower(), chunk.lower()) >= self.fuzzy_threshold:
                return True

        return False

    def get_keyword_priority(self, keyword: str) -> int:
        """Get priority for a keyword"""
        return self.keywords.get(keyword, 0)

    def filter_by_keywords(self, tenders: List[Dict], min_keywords: int = 1) -> List[Dict]:
        """
        Filter tenders that match minimum number of keywords

        Args:
            tenders: List of tender dictionaries
            min_keywords: Minimum number of keywords required

        Returns:
            Filtered list of tenders
        """
        filtered = []

        for tender in tenders:
            text = f"{tender.get('title', '')} {tender.get('description', '')}"
            matched = self.match_keywords(text)

            if len(matched) >= min_keywords:
                tender['matched_keywords'] = matched
                filtered.append(tender)

        return filtered

    def get_keyword_stats(self, tenders: List[Dict]) -> Dict[str, int]:
        """
        Get statistics on keyword occurrences

        Args:
            tenders: List of tenders with matched_keywords

        Returns:
            Dictionary of keyword counts
        """
        stats = {}

        for tender in tenders:
            keywords = tender.get('matched_keywords', [])
            for keyword in keywords:
                stats[keyword] = stats.get(keyword, 0) + 1

        # Sort by count
        return dict(sorted(stats.items(), key=lambda x: x[1], reverse=True))

    def highlight_keywords(self, text: str) -> str:
        """
        Highlight matched keywords in text with HTML tags

        Args:
            text: Text to highlight

        Returns:
            HTML with highlighted keywords
        """
        if not text:
            return ""

        highlighted = text
        matched = self.match_keywords(text)

        for keyword in matched:
            # Case-insensitive replacement with HTML highlight
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            highlighted = pattern.sub(
                f'<mark class="keyword-highlight">{keyword}</mark>',
                highlighted
            )

        return highlighted
