"""
Configuration settings for Tender Intelligence Platform
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "Tender Intelligence Platform"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Security
    SECRET_KEY: str = "your-secure-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/tenderdb"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 3600  # 1 hour

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Crawler Settings
    GEM_MAX_PAGES: int = 20
    CPPP_MAX_PAGES: int = 15
    TENDER247_MAX_PAGES: int = 10
    TENDERTIGER_MAX_PAGES: int = 10
    TENDERDETAIL_MAX_PAGES: int = 10

    CRAWLER_TIMEOUT: int = 30
    CRAWLER_MAX_RETRIES: int = 3
    CRAWLER_CONCURRENCY: int = 5

    # User Agents
    USER_AGENTS: list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    ]

    # Proxy Settings (optional)
    USE_PROXY: bool = False
    PROXY_URL: Optional[str] = None

    # Email Settings (for notifications)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: str = "noreply@tenderintel.com"

    # Frontend
    CORS_ORIGINS: list = ["http://localhost:8000", "http://localhost:3000"]

    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # Monitoring
    ENABLE_METRICS: bool = True
    SENTRY_DSN: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


# MDM Keywords Configuration with priorities
MDM_KEYWORDS = {
    "master data management": 10,
    "material codification": 10,
    "data governance": 9,
    "vendor data governance": 9,
    "data cleansing": 8,
    "data enrichment": 8,
    "material master": 8,
    "asset master": 8,
    "cataloguing": 7,
    "data standardization": 7,
    "service master": 7,
    "bill of material": 7,
    "bom": 6,
    "maximo": 6,
    "estring": 6,
    "spares": 5,
    "materials": 5,
    "services": 5,
}


# Tender Sources Configuration
TENDER_SOURCES = {
    "gem": {
        "name": "GEM BidPlus",
        "url": "https://bidplus.gem.gov.in/all-bids",
        "enabled": True,
        "priority": 1
    },
    "cppp": {
        "name": "CPPP eProcurement",
        "url": "https://eprocure.gov.in/cppp/",
        "enabled": True,
        "priority": 2
    },
    "tenderontime": {
        "name": "Tender On Time",
        "url": "https://www.tenderontime.com/",
        "enabled": True,
        "priority": 3
    },
    "tender247": {
        "name": "Tender247",
        "url": "https://www.tender247.com/",
        "enabled": True,
        "priority": 4
    },
    "tenderdetail": {
        "name": "TenderDetail",
        "url": "https://www.tenderdetail.com/",
        "enabled": True,
        "priority": 5
    },
    "tendertiger": {
        "name": "TenderTiger",
        "url": "https://www.tendertiger.com/",
        "enabled": True,
        "priority": 6
    }
}
