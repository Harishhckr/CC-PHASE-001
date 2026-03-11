from datetime import datetime, timedelta

from flask import Blueprint, current_app, jsonify, render_template, request
from sqlalchemy import func

from .extensions import cache, db
from .models import ScrapeLog, Tender


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@cache.cached(timeout=120)

def index():
    query = Tender.query
    search = request.args.get("search")
    source = request.args.get("source")
    min_score = request.args.get("min_score")

    if search:
        query = query.filter(Tender.description.ilike(f"%{search}%"))
    if source:
        query = query.filter(Tender.source == source)
    if min_score:
        try:
            min_score_value = float(min_score)
            query = query.filter(Tender.relevance_score >= min_score_value)
        except ValueError:
            pass

    tenders = query.order_by(Tender.end_date.desc().nullslast()).limit(200).all()
    sources = [row[0] for row in db.session.query(Tender.source).distinct().all()]
    return render_template("dashboard.html", tenders=tenders, sources=sources)


@dashboard_bp.route("/api/analytics")
@cache.cached(timeout=120)

def analytics():
    last_week = datetime.utcnow() - timedelta(days=7)
    total = Tender.query.count()
    avg_score = db.session.query(func.avg(Tender.relevance_score)).scalar() or 0
    recent = Tender.query.filter(Tender.created_at >= last_week).count()
    sources = (
        db.session.query(Tender.source, func.count(Tender.id))
        .group_by(Tender.source)
        .order_by(func.count(Tender.id).desc())
        .all()
    )
    score_buckets = {
        "high": Tender.query.filter(Tender.relevance_score >= 70).count(),
        "mid": Tender.query.filter(
            Tender.relevance_score >= 40,
            Tender.relevance_score < 70,
        ).count(),
        "low": Tender.query.filter(Tender.relevance_score < 40).count(),
    }
    logs = (
        ScrapeLog.query.order_by(ScrapeLog.created_at.desc())
        .limit(10)
        .all()
    )
    return jsonify(
        {
            "total": total,
            "average_score": round(avg_score, 2),
            "recent": recent,
            "sources": [{"source": row[0], "count": row[1]} for row in sources],
            "score_buckets": score_buckets,
            "logs": [
                {
                    "source": log.source,
                    "status": log.status,
                    "message": log.message,
                    "created_at": log.created_at.isoformat(),
                }
                for log in logs
            ],
        }
    )


@dashboard_bp.route("/health")

def health():
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()})
