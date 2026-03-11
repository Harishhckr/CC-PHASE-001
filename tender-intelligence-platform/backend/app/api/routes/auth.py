from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.config import get_settings
from app.database.models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])

settings = get_settings()


class RegisterRequest(BaseModel):
    username: str
    email: str
    full_name: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


@router.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db_session)):
    user = User(
        username=payload.username,
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=f"hashed-{payload.password}",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/token", response_model=TokenResponse)
def login(username: str, password: str):
    if not username or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")
    expires = timedelta(minutes=settings.access_token_expire_minutes)
    return TokenResponse(access_token=f"token-{username}", expires_in=int(expires.total_seconds()))


@router.get("/me")
def me(db: Session = Depends(get_db_session)):
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
