import enum
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class TenderSource(str, enum.Enum):
    gem = "gem"
    cppp = "cppp"
    tenderontime = "tenderontime"
    tender247 = "tender247"
    tenderdetail = "tenderdetail"
    tendertiger = "tendertiger"


class TenderStatus(str, enum.Enum):
    active = "active"
    closed = "closed"
    cancelled = "cancelled"


class Tender(Base):
    __tablename__ = "tenders"

    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(String, nullable=False)
    source = Column(Enum(TenderSource), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    buyer = Column(String, nullable=True)
    value = Column(Float, nullable=True)
    currency = Column(String, default="INR", nullable=False)
    location = Column(String, nullable=True)
    matched_keywords = Column(JSON, default=list)
    relevance_score = Column(Float, default=0.0)
    status = Column(Enum(TenderStatus), default=TenderStatus.active)
    document_link = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    alerts = relationship("Alert", back_populates="tender")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    preferred_keywords = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    alerts = relationship("Alert", back_populates="user")


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=True)
    priority = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tender_id = Column(Integer, ForeignKey("tenders.id"), nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="alerts")
    tender = relationship("Tender", back_populates="alerts")
