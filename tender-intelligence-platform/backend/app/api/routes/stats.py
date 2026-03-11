from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.database.queries import get_keyword_stats, get_recent_trends, get_source_distribution

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/dashboard")
def dashboard_stats(db: Session = Depends(get_db_session)):
    return {
        "sources": get_source_distribution(db),
        "trends": get_recent_trends(db),
    }


@router.get("/trends")
def trends(db: Session = Depends(get_db_session)):
    return get_recent_trends(db)


@router.get("/sources")
def sources(db: Session = Depends(get_db_session)):
    return get_source_distribution(db)


@router.get("/keywords")
def keywords(db: Session = Depends(get_db_session)):
    return get_keyword_stats(db)
