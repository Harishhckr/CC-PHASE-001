from __future__ import annotations

from celery import Celery
from flask import Flask

from .config import Config
from .extensions import db
from .models import ScrapeLog, Tender
from .scrapers import get_scrapers
from .services import calculate_relevance, load_keywords


celery_app = Celery("tender_intel")
celery_app.config_from_object(Config)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app


@celery_app.task

def run_scrapers() -> dict[str, int]:
    app = create_app()
    keywords = load_keywords(app.config["MDM_KEYWORDS_FILE"])
    results = {"created": 0, "updated": 0, "filtered": 0}

    with app.app_context():
        for scraper in get_scrapers(app.config["SCRAPER_USER_AGENT"]):
            try:
                created = 0
                updated = 0
                filtered = 0
                payloads = scraper.run()
                for payload in payloads:
                    result = calculate_relevance(payload.description, keywords)
                    if keywords and not result.matched_keywords:
                        filtered += 1
                        results["filtered"] += 1
                        continue
                    tender = Tender.query.filter_by(tender_id=payload.tender_id).first()
                    if tender:
                        tender.description = payload.description
                        tender.start_date = payload.start_date
                        tender.end_date = payload.end_date
                        tender.document_links = payload.document_links
                        tender.relevance_score = result.score
                        tender.keywords_matched = result.matched_keywords
                        tender.source = payload.source
                        updated += 1
                        results["updated"] += 1
                    else:
                        tender = Tender(
                            tender_id=payload.tender_id,
                            description=payload.description,
                            start_date=payload.start_date,
                            end_date=payload.end_date,
                            document_links=payload.document_links,
                            relevance_score=result.score,
                            keywords_matched=result.matched_keywords,
                            source=payload.source,
                        )
                        db.session.add(tender)
                        created += 1
                        results["created"] += 1
                db.session.add(
                    ScrapeLog(
                        source=scraper.source,
                        status="success",
                        message=(
                            "Scrape completed: "
                            f"created={created}, updated={updated}, filtered={filtered}"
                        ),
                    )
                )
                db.session.commit()
            except Exception as exc:
                db.session.rollback()
                db.session.add(
                    ScrapeLog(source=scraper.source, status="failed", message=str(exc))
                )
                db.session.commit()
    return results
