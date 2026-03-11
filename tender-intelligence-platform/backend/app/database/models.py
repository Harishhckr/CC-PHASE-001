"""
Database models for Tender Intelligence Platform
"""
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, Boolean,
    ForeignKey, JSON, Enum, UniqueConstraint, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum


Base = declarative_base()


class TenderStatus(str, enum.Enum):
    """Tender status enumeration"""
    ACTIVE = "active"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class TenderSource(str, enum.Enum):
    """Tender source enumeration"""
    GEM = "gem"
    CPPP = "cppp"
    TENDERONTIME = "tenderontime"
    TENDER247 = "tender247"
    TENDERDETAIL = "tenderdetail"
    TENDERTIGER = "tendertiger"


class Tender(Base):
    """Tender model"""
    __tablename__ = "tenders"

    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(String(255), nullable=False, index=True)
    source = Column(Enum(TenderSource), nullable=False, index=True)

    title = Column(String(500), nullable=False)
    description = Column(Text)

    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True, index=True)

    buyer = Column(String(255))
    value = Column(Float, nullable=True)
    currency = Column(String(10), default="INR")
    location = Column(String(255), index=True)

    matched_keywords = Column(JSON, default=list)
    relevance_score = Column(Float, default=0.0, index=True)

    status = Column(Enum(TenderStatus), default=TenderStatus.ACTIVE, index=True)
    document_link = Column(String(500))

    duplicate_group_id = Column(Integer, nullable=True, index=True)
    is_duplicate = Column(Boolean, default=False)

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    alerts = relationship("Alert", back_populates="tender", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="tender", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        UniqueConstraint('tender_id', 'source', name='uq_tender_source'),
        Index('idx_relevance_score', 'relevance_score'),
        Index('idx_end_date_status', 'end_date', 'status'),
    )

    def __repr__(self):
        return f"<Tender(id={self.id}, tender_id={self.tender_id}, source={self.source})>"


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255))
    hashed_password = Column(String(255), nullable=False)

    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    preferred_keywords = Column(JSON, default=list)
    preferred_locations = Column(JSON, default=list)

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


class Keyword(Base):
    """Keyword model for MDM keywords"""
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(255), unique=True, nullable=False, index=True)
    category = Column(String(100), index=True)
    priority = Column(Integer, default=5)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Keyword(id={self.id}, keyword={self.keyword}, priority={self.priority})>"


class Alert(Base):
    """Alert model for user notifications"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    tender_id = Column(Integer, ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False, index=True)

    is_read = Column(Boolean, default=False, index=True)
    alert_type = Column(String(50), default="new_tender")  # new_tender, expiring_soon, high_relevance

    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="alerts")
    tender = relationship("Tender", back_populates="alerts")

    def __repr__(self):
        return f"<Alert(id={self.id}, user_id={self.user_id}, tender_id={self.tender_id})>"


class Bookmark(Base):
    """Bookmark model for saved tenders"""
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    tender_id = Column(Integer, ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False, index=True)

    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="bookmarks")
    tender = relationship("Tender", back_populates="bookmarks")

    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'tender_id', name='uq_user_tender_bookmark'),
    )

    def __repr__(self):
        return f"<Bookmark(id={self.id}, user_id={self.user_id}, tender_id={self.tender_id})>"


class CrawlerStats(Base):
    """Crawler statistics model"""
    __tablename__ = "crawler_stats"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(Enum(TenderSource), nullable=False, index=True)

    crawl_started_at = Column(DateTime, nullable=False)
    crawl_completed_at = Column(DateTime, nullable=True)

    total_processed = Column(Integer, default=0)
    total_saved = Column(Integer, default=0)
    total_duplicates = Column(Integer, default=0)
    total_errors = Column(Integer, default=0)

    status = Column(String(50), default="running")  # running, completed, failed
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=func.now(), nullable=False)

    def __repr__(self):
        return f"<CrawlerStats(id={self.id}, source={self.source}, status={self.status})>"
