"""
Deduplicator for identifying and merging duplicate tenders
"""
from typing import List, Dict, Tuple
from fuzzywuzzy import fuzz
from loguru import logger
from sqlalchemy.orm import Session
from app.database.models import Tender


class Deduplicator:
    """Duplicate detection and management"""

    def __init__(self, title_threshold: int = 85, description_threshold: int = 80):
        """
        Initialize deduplicator

        Args:
            title_threshold: Minimum fuzzy match score for titles (0-100)
            description_threshold: Minimum fuzzy match score for descriptions (0-100)
        """
        self.title_threshold = title_threshold
        self.description_threshold = description_threshold

    def is_duplicate(self, tender1: Dict, tender2: Dict) -> bool:
        """
        Check if two tenders are duplicates

        Args:
            tender1: First tender dictionary
            tender2: Second tender dictionary

        Returns:
            True if duplicates
        """
        # Exact match on tender_id and source
        if (tender1.get("tender_id") == tender2.get("tender_id") and
            tender1.get("source") == tender2.get("source")):
            return True

        # Fuzzy match on title
        title1 = tender1.get("title", "")
        title2 = tender2.get("title", "")

        if title1 and title2:
            title_score = fuzz.ratio(title1.lower(), title2.lower())
            if title_score >= self.title_threshold:
                return True

        # Fuzzy match on description (if titles are similar)
        desc1 = tender1.get("description", "")
        desc2 = tender2.get("description", "")

        if desc1 and desc2:
            desc_score = fuzz.ratio(desc1.lower(), desc2.lower())
            if desc_score >= self.description_threshold:
                return True

        return False

    def find_duplicates(self, tenders: List[Dict]) -> List[List[Dict]]:
        """
        Find all duplicate groups in a list of tenders

        Args:
            tenders: List of tender dictionaries

        Returns:
            List of duplicate groups (each group is a list of duplicate tenders)
        """
        duplicate_groups = []
        processed = set()

        for i, tender1 in enumerate(tenders):
            if i in processed:
                continue

            group = [tender1]

            for j, tender2 in enumerate(tenders[i + 1:], start=i + 1):
                if j in processed:
                    continue

                if self.is_duplicate(tender1, tender2):
                    group.append(tender2)
                    processed.add(j)

            if len(group) > 1:
                duplicate_groups.append(group)
                processed.add(i)

        return duplicate_groups

    def merge_duplicates(self, duplicates: List[Dict]) -> Dict:
        """
        Merge duplicate tenders into one, keeping best data

        Strategy:
        - Keep highest relevance score
        - Combine matched keywords (unique)
        - Keep longest description
        - Prefer GEM source over others

        Args:
            duplicates: List of duplicate tender dictionaries

        Returns:
            Merged tender dictionary
        """
        if not duplicates:
            return {}

        if len(duplicates) == 1:
            return duplicates[0]

        # Sort by relevance score (highest first)
        sorted_duplicates = sorted(
            duplicates,
            key=lambda x: x.get("relevance_score", 0),
            reverse=True
        )

        # Start with highest scoring tender
        merged = sorted_duplicates[0].copy()

        # Combine matched keywords (unique)
        all_keywords = set()
        for dup in sorted_duplicates:
            keywords = dup.get("matched_keywords", [])
            all_keywords.update(keywords)
        merged["matched_keywords"] = list(all_keywords)

        # Keep longest description
        longest_desc = max(
            (d.get("description", "") for d in sorted_duplicates),
            key=len,
            default=""
        )
        merged["description"] = longest_desc

        # Prefer GEM source
        gem_tender = next((d for d in sorted_duplicates if d.get("source") == "gem"), None)
        if gem_tender:
            merged["source"] = gem_tender["source"]
            merged["tender_id"] = gem_tender["tender_id"]

        # Mark as deduplicated
        merged["is_duplicate"] = False

        logger.info(f"Merged {len(duplicates)} duplicate tenders into one")
        return merged

    def mark_duplicates_in_db(self, db: Session) -> int:
        """
        Find and mark duplicates in database

        Args:
            db: Database session

        Returns:
            Number of duplicates marked
        """
        try:
            # Get all active tenders
            tenders = db.query(Tender).filter(
                Tender.is_duplicate == False
            ).all()

            # Convert to dictionaries
            tender_dicts = [
                {
                    "id": t.id,
                    "tender_id": t.tender_id,
                    "source": t.source.value if hasattr(t.source, 'value') else t.source,
                    "title": t.title,
                    "description": t.description,
                    "relevance_score": t.relevance_score
                }
                for t in tenders
            ]

            # Find duplicate groups
            duplicate_groups = self.find_duplicates(tender_dicts)

            marked_count = 0
            for group_id, group in enumerate(duplicate_groups, start=1):
                # Keep the first one (highest relevance), mark others as duplicates
                for tender_dict in group[1:]:
                    tender = db.query(Tender).filter(Tender.id == tender_dict["id"]).first()
                    if tender:
                        tender.is_duplicate = True
                        tender.duplicate_group_id = group_id
                        marked_count += 1

            db.commit()
            logger.info(f"Marked {marked_count} tenders as duplicates in {len(duplicate_groups)} groups")
            return marked_count

        except Exception as e:
            db.rollback()
            logger.error(f"Error marking duplicates: {e}")
            return 0
