# Tender Intelligence Platform

## Overview
A production-ready tender intelligence system with:
- Multi-portal scraping (CPP, GeM, State portals)
- MDM keyword filtering and relevance scoring
- PostgreSQL persistence
- Redis caching and Celery scheduling
- Professional dashboard with analytics and dark mode

## Quickstart
1. Configure environment variables:
   - `DATABASE_URL` (PostgreSQL)
   - `REDIS_URL` (Redis)
   - `SECRET_KEY`
   - `MDM_KEYWORDS_FILE` (defaults to `CAD_Phase1.rtf.docx`)
2. Run the web app: `python app/main.py`
3. Run celery worker: `celery -A app.tasks.celery_app worker -B --loglevel=info`

## Notes
- Update scraper URLs and selectors per portal requirements.
- Ensure `CAD_Phase1.rtf.docx` contains comma-separated keywords.
