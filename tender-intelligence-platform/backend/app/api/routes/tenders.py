from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.database.queries import (
    get_expiring_tenders,
    get_similar_tenders,
    get_tender_by_id,
    get_tenders,
    get_today_tenders,
    search_tenders,
)

router = APIRouter(prefix="/api/tenders", tags=["tenders"])


@router.get("")
def list_tenders(skip: int = 0, limit: int = 50, db: Session = Depends(get_db_session)):
    return get_tenders(db, skip=skip, limit=limit)


@router.get("/search")
def search_tenders_api(query: str, skip: int = 0, limit: int = 50, db: Session = Depends(get_db_session)):
    return search_tenders(db, query, skip=skip, limit=limit)


@router.get("/today")
def today_tenders(db: Session = Depends(get_db_session)):
    return get_today_tenders(db)


@router.get("/expiring")
def expiring_tenders(db: Session = Depends(get_db_session)):
    return get_expiring_tenders(db)


@router.get("/{tender_id}")
def get_tender(tender_id: int, db: Session = Depends(get_db_session)):
    tender = get_tender_by_id(db, tender_id)
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    return tender


@router.get("/{tender_id}/similar")
def similar_tenders(tender_id: int, db: Session = Depends(get_db_session)):
    tender = get_tender_by_id(db, tender_id)
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    return get_similar_tenders(db, tender)


@router.post("/{tender_id}/bookmark")
def bookmark_tender(tender_id: int):
    return {"status": "bookmarked", "tender_id": tender_id}


@router.get("/export/csv")
def export_csv():
    return {"status": "queued", "format": "csv"}
