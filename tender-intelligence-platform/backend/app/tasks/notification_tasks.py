from celery import shared_task
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.database.models import User
from app.database.queries import get_today_tenders
from app.services.notification import build_daily_digest


@shared_task(name="app.tasks.notification_tasks.send_daily_digest")
def send_daily_digest():
    db: Session = SessionLocal()
    try:
        users = db.query(User).all()
        tenders = get_today_tenders(db)
        return [build_daily_digest(user, tenders) for user in users]
    finally:
        db.close()
