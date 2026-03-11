from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.models import Alert, Keyword, Tender, TenderSource, TenderStatus, User


def get_tenders(db: Session, skip: int = 0, limit: int = 50) -> List[Tender]:
    return db.query(Tender).order_by(Tender.created_at.desc()).offset(skip).limit(limit).all()


def search_tenders(db: Session, query: str, skip: int = 0, limit: int = 50) -> List[Tender]:
    return (
        db.query(Tender)
        .filter(Tender.description.ilike(f"%{query}%"))
        .order_by(Tender.relevance_score.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_today_tenders(db: Session) -> List[Tender]:
    today = datetime.utcnow().date()
    return db.query(Tender).filter(func.date(Tender.created_at) == today).all()


def get_expiring_tenders(db: Session, days: int = 3) -> List[Tender]:
    threshold = datetime.utcnow() + timedelta(days=days)
    return (
        db.query(Tender)
        .filter(Tender.end_date <= threshold, Tender.status == TenderStatus.active)
        .order_by(Tender.end_date.asc())
        .all()
    )


def get_tender_by_id(db: Session, tender_id: int) -> Optional[Tender]:
    return db.query(Tender).filter(Tender.id == tender_id).first()


def get_similar_tenders(db: Session, tender: Tender, limit: int = 5) -> List[Tender]:
    return (
        db.query(Tender)
        .filter(Tender.id != tender.id, Tender.source == tender.source)
        .order_by(Tender.relevance_score.desc())
        .limit(limit)
        .all()
    )


def get_unread_alerts(db: Session, user_id: int) -> List[Alert]:
    return db.query(Alert).filter(Alert.user_id == user_id, Alert.is_read.is_(False)).all()


def get_keywords(db: Session) -> List[Keyword]:
    return db.query(Keyword).filter(Keyword.is_active.is_(True)).all()


def get_source_distribution(db: Session):
    return db.query(Tender.source, func.count(Tender.id)).group_by(Tender.source).all()


def get_recent_trends(db: Session, days: int = 7):
    start_date = datetime.utcnow() - timedelta(days=days)
    return (
        db.query(func.date(Tender.created_at), func.count(Tender.id))
        .filter(Tender.created_at >= start_date)
        .group_by(func.date(Tender.created_at))
        .all()
    )


def get_keyword_stats(db: Session):
    return db.query(Keyword.keyword, Keyword.priority).all()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def create_alert(db: Session, user_id: int, tender_id: int) -> Alert:
    alert = Alert(user_id=user_id, tender_id=tender_id)
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert
