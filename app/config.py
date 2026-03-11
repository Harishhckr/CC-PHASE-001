import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "postgresql+psycopg2://tender:password@localhost:5432/tenders"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", "300"))
    SCHEDULER_CRON = os.getenv("SCHEDULER_CRON", "0 */6 * * *")
    MDM_KEYWORDS_FILE = os.getenv("MDM_KEYWORDS_FILE", "CAD_Phase1.rtf.docx")
    SCRAPER_USER_AGENT = os.getenv(
        "SCRAPER_USER_AGENT",
        "TenderIntelBot/1.0 (+https://example.com/contact)",
    )
