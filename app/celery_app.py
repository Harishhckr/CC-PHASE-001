from celery.schedules import crontab

from .config import Config
from .tasks import celery_app, run_scrapers


celery_app.conf.beat_schedule = {
    "scheduled-scrape": {
        "task": "app.tasks.run_scrapers",
        "schedule": crontab(minute=0, hour="*/6"),
    }
}

celery_app.conf.timezone = "Asia/Kolkata"
