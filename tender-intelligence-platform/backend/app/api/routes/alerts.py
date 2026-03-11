from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db_session
from app.database.queries import create_alert, get_unread_alerts

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("")
def list_alerts(db: Session = Depends(get_db_session), user=Depends(get_current_user)):
    return get_unread_alerts(db, user.id)


@router.post("/{alert_id}/read")
def mark_read(alert_id: int):
    return {"status": "read", "alert_id": alert_id}


@router.get("/count")
def unread_count(db: Session = Depends(get_db_session), user=Depends(get_current_user)):
    return {"count": len(get_unread_alerts(db, user.id))}


@router.post("")
def create(alert_tender_id: int, db: Session = Depends(get_db_session), user=Depends(get_current_user)):
    return create_alert(db, user.id, alert_tender_id)
