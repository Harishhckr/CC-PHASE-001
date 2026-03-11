from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.queries import get_user_by_username


def get_db_session() -> Session:
    return next(get_db())


def get_current_user(db: Session = Depends(get_db_session)):
    user = get_user_by_username(db, "demo")
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user
