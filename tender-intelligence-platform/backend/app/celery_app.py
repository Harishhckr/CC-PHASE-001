from celery import Celery
from celery.schedules import crontab

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "tender-intelligence",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.crawler_tasks", "app.tasks.notification_tasks"],
)

celery_app.conf.beat_schedule = {
    "crawl-gem": {
        "task": "app.tasks.crawler_tasks.crawl_gem",
        "schedule": crontab(minute="*/30"),
    },
    "crawl-cppp": {
        "task": "app.tasks.crawler_tasks.crawl_cppp",
        "schedule": crontab(minute=0),
    },
    "crawl-tender247": {
        "task": "app.tasks.crawler_tasks.crawl_tender247",
        "schedule": crontab(minute=0, hour="*/2"),
    },
    "crawl-tendertiger": {
        "task": "app.tasks.crawler_tasks.crawl_tendertiger",
        "schedule": crontab(minute=0, hour="*/3"),
    },
    "crawl-tenderdetail": {
        "task": "app.tasks.crawler_tasks.crawl_tenderdetail",
        "schedule": crontab(minute=0, hour="*/4"),
    },
    "daily-digest": {
        "task": "app.tasks.notification_tasks.send_daily_digest",
        "schedule": crontab(hour=8, minute=0),
    },
}
