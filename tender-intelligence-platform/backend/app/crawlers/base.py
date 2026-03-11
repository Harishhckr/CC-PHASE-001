"""
Base crawler class with common functionality
"""
import random
import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger
from sqlalchemy.orm import Session

from app.config import settings
from app.database.connection import get_db_context
from app.database.models import Tender, CrawlerStats, TenderSource
from app.processors.normalizer import DataNormalizer
from app.processors.keyword_filter import KeywordFilter
from app.processors.relevance_scorer import RelevanceScorer
from app.processors.deduplicator import Deduplicator


class BaseCrawler(ABC):
    """Base crawler class for all tender sources"""

    def __init__(self, source: TenderSource):
        self.source = source
        self.user_agents = settings.USER_AGENTS
        self.timeout = settings.CRAWLER_TIMEOUT
        self.max_retries = settings.CRAWLER_MAX_RETRIES

        # Processors
        self.normalizer = DataNormalizer()
        self.keyword_filter = KeywordFilter()
        self.relevance_scorer = RelevanceScorer()
        self.deduplicator = Deduplicator()

        # Statistics
        self.stats = {
            "total_processed": 0,
            "total_saved": 0,
            "total_duplicates": 0,
            "total_errors": 0,
            "start_time": None,
            "end_time": None
        }

    def get_random_user_agent(self) -> str:
        """Get random user agent"""
        return random.choice(self.user_agents)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def fetch_with_retry(self, url: str, **kwargs) -> Any:
        """Fetch URL with retry logic"""
        pass  # To be implemented by specific crawlers

    @abstractmethod
    async def crawl(self) -> List[Dict[str, Any]]:
        """Main crawl method - must be implemented by subclasses"""
        pass

    def normalize_tender_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize raw tender data"""
        try:
            normalized = {
                "tender_id": self.normalizer.clean_text(str(raw_data.get("tender_id", ""))),
                "source": self.source,
                "title": self.normalizer.clean_text(raw_data.get("title", "")),
                "description": self.normalizer.clean_text(raw_data.get("description", "")),
                "start_date": self.normalizer.parse_date(raw_data.get("start_date")),
                "end_date": self.normalizer.parse_date(raw_data.get("end_date")),
                "buyer": self.normalizer.clean_text(raw_data.get("buyer", "")),
                "value": self.normalizer.parse_currency(raw_data.get("value")),
                "currency": raw_data.get("currency", "INR"),
                "location": self.normalizer.clean_text(raw_data.get("location", "")),
                "document_link": raw_data.get("document_link", ""),
                "status": raw_data.get("status", "active")
            }
            return normalized
        except Exception as e:
            logger.error(f"Error normalizing tender data: {e}")
            self.stats["total_errors"] += 1
            return None

    def process_tender(self, tender_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process tender through all filters and scoring"""
        try:
            # Normalize data
            normalized = self.normalize_tender_data(tender_data)
            if not normalized:
                return None

            # Filter by keywords
            text_to_filter = f"{normalized['title']} {normalized['description']}"
            matched_keywords = self.keyword_filter.match_keywords(text_to_filter)

            # Skip if no keywords matched
            if not matched_keywords:
                logger.debug(f"No MDM keywords matched for tender: {normalized['tender_id']}")
                return None

            # Calculate relevance score
            relevance_score = self.relevance_scorer.calculate_score(
                matched_keywords=matched_keywords,
                tender_value=normalized.get("value", 0),
                end_date=normalized.get("end_date"),
                location=normalized.get("location")
            )

            # Add matched keywords and score
            normalized["matched_keywords"] = matched_keywords
            normalized["relevance_score"] = relevance_score

            self.stats["total_processed"] += 1
            return normalized

        except Exception as e:
            logger.error(f"Error processing tender: {e}")
            self.stats["total_errors"] += 1
            return None

    def save_tender(self, db: Session, tender_data: Dict[str, Any]) -> Optional[Tender]:
        """Save tender to database"""
        try:
            # Check for duplicates
            existing = db.query(Tender).filter(
                Tender.tender_id == tender_data["tender_id"],
                Tender.source == tender_data["source"]
            ).first()

            if existing:
                logger.debug(f"Duplicate tender found: {tender_data['tender_id']}")
                self.stats["total_duplicates"] += 1
                return None

            # Create new tender
            tender = Tender(**tender_data)
            db.add(tender)
            db.commit()
            db.refresh(tender)

            self.stats["total_saved"] += 1
            logger.info(f"Saved tender: {tender.tender_id} (Score: {tender.relevance_score:.2f})")
            return tender

        except Exception as e:
            db.rollback()
            logger.error(f"Error saving tender: {e}")
            self.stats["total_errors"] += 1
            return None

    def save_crawler_stats(self, db: Session, status: str = "completed", error_message: str = None):
        """Save crawler statistics"""
        try:
            stats = CrawlerStats(
                source=self.source,
                crawl_started_at=self.stats["start_time"],
                crawl_completed_at=self.stats["end_time"],
                total_processed=self.stats["total_processed"],
                total_saved=self.stats["total_saved"],
                total_duplicates=self.stats["total_duplicates"],
                total_errors=self.stats["total_errors"],
                status=status,
                error_message=error_message
            )
            db.add(stats)
            db.commit()
            logger.info(f"Crawler stats saved for {self.source}")
        except Exception as e:
            logger.error(f"Error saving crawler stats: {e}")

    async def run(self) -> Dict[str, Any]:
        """Run the crawler and process all tenders"""
        self.stats["start_time"] = datetime.now()
        logger.info(f"Starting crawler for {self.source}")

        try:
            # Crawl tenders
            raw_tenders = await self.crawl()
            logger.info(f"Crawled {len(raw_tenders)} raw tenders from {self.source}")

            # Process and save tenders
            with get_db_context() as db:
                for raw_tender in raw_tenders:
                    processed = self.process_tender(raw_tender)
                    if processed:
                        self.save_tender(db, processed)

                # Save crawler statistics
                self.stats["end_time"] = datetime.now()
                self.save_crawler_stats(db, status="completed")

            logger.info(
                f"Crawler finished for {self.source}: "
                f"Processed={self.stats['total_processed']}, "
                f"Saved={self.stats['total_saved']}, "
                f"Duplicates={self.stats['total_duplicates']}, "
                f"Errors={self.stats['total_errors']}"
            )

            return self.stats

        except Exception as e:
            self.stats["end_time"] = datetime.now()
            logger.error(f"Crawler failed for {self.source}: {e}")

            with get_db_context() as db:
                self.save_crawler_stats(db, status="failed", error_message=str(e))

            return self.stats
