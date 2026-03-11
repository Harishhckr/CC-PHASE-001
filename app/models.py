from datetime import datetime

from .extensions import db


class Tender(db.Model):
    __tablename__ = "tenders"

    id = db.Column(db.Integer, primary_key=True)
    tender_id = db.Column(db.String(128), unique=True, nullable=False)
    source = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    document_links = db.Column(db.JSON, nullable=False, default=list)
    relevance_score = db.Column(db.Float, nullable=False, default=0.0)
    keywords_matched = db.Column(db.JSON, nullable=False, default=list)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ScrapeLog(db.Model):
    __tablename__ = "scrape_logs"

    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(128), nullable=False)
    status = db.Column(db.String(32), nullable=False)
    message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
