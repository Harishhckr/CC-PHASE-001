"""
Reusable database queries
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from app.database.models import Tender, User, Keyword, Alert, Bookmark, CrawlerStats, TenderStatus
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any


class TenderQueries:
    """Tender-related database queries"""

    @staticmethod
    def get_tender_by_id(db: Session, tender_id: int) -> Optional[Tender]:
        """Get tender by ID"""
        return db.query(Tender).filter(Tender.id == tender_id).first()

    @staticmethod
    def get_tender_by_source_id(db: Session, tender_id: str, source: str) -> Optional[Tender]:
        """Get tender by source ID"""
        return db.query(Tender).filter(
            and_(Tender.tender_id == tender_id, Tender.source == source)
        ).first()

    @staticmethod
    def get_tenders_paginated(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
        source: Optional[str] = None,
        min_relevance: float = 0.0
    ) -> List[Tender]:
        """Get paginated tenders with filters"""
        query = db.query(Tender).filter(Tender.relevance_score >= min_relevance)

        if status:
            query = query.filter(Tender.status == status)
        if source:
            query = query.filter(Tender.source == source)

        return query.order_by(desc(Tender.created_at)).offset(skip).limit(limit).all()

    @staticmethod
    def search_tenders(
        db: Session,
        search_query: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[Tender]:
        """Search tenders by text"""
        search_pattern = f"%{search_query}%"
        return db.query(Tender).filter(
            or_(
                Tender.title.ilike(search_pattern),
                Tender.description.ilike(search_pattern),
                Tender.buyer.ilike(search_pattern)
            )
        ).order_by(desc(Tender.relevance_score)).offset(skip).limit(limit).all()

    @staticmethod
    def get_todays_tenders(db: Session) -> List[Tender]:
        """Get tenders created today"""
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return db.query(Tender).filter(
            Tender.created_at >= today_start
        ).order_by(desc(Tender.relevance_score)).all()

    @staticmethod
    def get_expiring_soon(db: Session, days: int = 7) -> List[Tender]:
        """Get tenders expiring soon"""
        now = datetime.now()
        future = now + timedelta(days=days)
        return db.query(Tender).filter(
            and_(
                Tender.end_date.between(now, future),
                Tender.status == TenderStatus.ACTIVE
            )
        ).order_by(Tender.end_date).all()

    @staticmethod
    def get_high_relevance_tenders(db: Session, threshold: float = 50.0, limit: int = 100) -> List[Tender]:
        """Get high relevance tenders"""
        return db.query(Tender).filter(
            Tender.relevance_score >= threshold
        ).order_by(desc(Tender.relevance_score)).limit(limit).all()

    @staticmethod
    def get_similar_tenders(db: Session, tender: Tender, limit: int = 5) -> List[Tender]:
        """Get similar tenders based on keywords and location"""
        if not tender.matched_keywords:
            return []

        return db.query(Tender).filter(
            and_(
                Tender.id != tender.id,
                Tender.matched_keywords.op('&&')(tender.matched_keywords)  # Array overlap
            )
        ).order_by(desc(Tender.relevance_score)).limit(limit).all()

    @staticmethod
    def count_tenders(
        db: Session,
        status: Optional[str] = None,
        source: Optional[str] = None
    ) -> int:
        """Count tenders with filters"""
        query = db.query(func.count(Tender.id))

        if status:
            query = query.filter(Tender.status == status)
        if source:
            query = query.filter(Tender.source == source)

        return query.scalar()

    @staticmethod
    def create_tender(db: Session, tender_data: Dict[str, Any]) -> Tender:
        """Create new tender"""
        tender = Tender(**tender_data)
        db.add(tender)
        db.commit()
        db.refresh(tender)
        return tender

    @staticmethod
    def update_tender(db: Session, tender_id: int, update_data: Dict[str, Any]) -> Optional[Tender]:
        """Update tender"""
        tender = TenderQueries.get_tender_by_id(db, tender_id)
        if tender:
            for key, value in update_data.items():
                setattr(tender, key, value)
            db.commit()
            db.refresh(tender)
        return tender


class UserQueries:
    """User-related database queries"""

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def create_user(db: Session, user_data: Dict[str, Any]) -> User:
        """Create new user"""
        user = User(**user_data)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


class AlertQueries:
    """Alert-related database queries"""

    @staticmethod
    def get_user_alerts(db: Session, user_id: int, unread_only: bool = False) -> List[Alert]:
        """Get user alerts"""
        query = db.query(Alert).filter(Alert.user_id == user_id)

        if unread_only:
            query = query.filter(Alert.is_read == False)

        return query.order_by(desc(Alert.created_at)).all()

    @staticmethod
    def count_unread_alerts(db: Session, user_id: int) -> int:
        """Count unread alerts"""
        return db.query(func.count(Alert.id)).filter(
            and_(Alert.user_id == user_id, Alert.is_read == False)
        ).scalar()

    @staticmethod
    def mark_alert_read(db: Session, alert_id: int) -> Optional[Alert]:
        """Mark alert as read"""
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if alert:
            alert.is_read = True
            db.commit()
            db.refresh(alert)
        return alert

    @staticmethod
    def create_alert(db: Session, user_id: int, tender_id: int, alert_type: str = "new_tender") -> Alert:
        """Create new alert"""
        alert = Alert(user_id=user_id, tender_id=tender_id, alert_type=alert_type)
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert


class BookmarkQueries:
    """Bookmark-related database queries"""

    @staticmethod
    def get_user_bookmarks(db: Session, user_id: int) -> List[Bookmark]:
        """Get user bookmarks"""
        return db.query(Bookmark).filter(Bookmark.user_id == user_id).order_by(
            desc(Bookmark.created_at)
        ).all()

    @staticmethod
    def create_bookmark(db: Session, user_id: int, tender_id: int, notes: str = None) -> Bookmark:
        """Create bookmark"""
        bookmark = Bookmark(user_id=user_id, tender_id=tender_id, notes=notes)
        db.add(bookmark)
        db.commit()
        db.refresh(bookmark)
        return bookmark

    @staticmethod
    def delete_bookmark(db: Session, user_id: int, tender_id: int) -> bool:
        """Delete bookmark"""
        bookmark = db.query(Bookmark).filter(
            and_(Bookmark.user_id == user_id, Bookmark.tender_id == tender_id)
        ).first()

        if bookmark:
            db.delete(bookmark)
            db.commit()
            return True
        return False


class StatsQueries:
    """Statistics queries"""

    @staticmethod
    def get_dashboard_stats(db: Session) -> Dict[str, Any]:
        """Get dashboard statistics"""
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = datetime.now() - timedelta(days=7)

        return {
            "total_tenders": db.query(func.count(Tender.id)).scalar(),
            "active_tenders": db.query(func.count(Tender.id)).filter(
                Tender.status == TenderStatus.ACTIVE
            ).scalar(),
            "todays_tenders": db.query(func.count(Tender.id)).filter(
                Tender.created_at >= today_start
            ).scalar(),
            "mdm_tenders": db.query(func.count(Tender.id)).filter(
                Tender.relevance_score >= 50.0
            ).scalar(),
            "expiring_soon": db.query(func.count(Tender.id)).filter(
                and_(
                    Tender.end_date.between(datetime.now(), datetime.now() + timedelta(days=7)),
                    Tender.status == TenderStatus.ACTIVE
                )
            ).scalar(),
            "active_sources": db.query(func.count(func.distinct(Tender.source))).scalar()
        }

    @staticmethod
    def get_source_distribution(db: Session) -> List[Dict[str, Any]]:
        """Get tender count by source"""
        results = db.query(
            Tender.source,
            func.count(Tender.id).label('count')
        ).group_by(Tender.source).all()

        return [{"source": r.source, "count": r.count} for r in results]

    @staticmethod
    def get_daily_trends(db: Session, days: int = 7) -> List[Dict[str, Any]]:
        """Get daily tender trends"""
        start_date = datetime.now() - timedelta(days=days)

        results = db.query(
            func.date(Tender.created_at).label('date'),
            func.count(Tender.id).label('count')
        ).filter(
            Tender.created_at >= start_date
        ).group_by(func.date(Tender.created_at)).order_by(func.date(Tender.created_at)).all()

        return [{"date": str(r.date), "count": r.count} for r in results]
