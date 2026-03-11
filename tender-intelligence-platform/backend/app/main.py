from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.routes import alerts, auth, stats, tenders

app = FastAPI(title="Tender Intelligence Platform")

app.include_router(tenders.router)
app.include_router(auth.router)
app.include_router(alerts.router)
app.include_router(stats.router)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR.parent / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/tenders", response_class=HTMLResponse)
def tenders_page(request: Request):
    return templates.TemplateResponse("tenders.html", {"request": request})


@app.get("/tenders/{tender_id}", response_class=HTMLResponse)
def tender_detail(request: Request, tender_id: int):
    return templates.TemplateResponse("tender_detail.html", {"request": request, "tender_id": tender_id})


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/reports", response_class=HTMLResponse)
def reports_page(request: Request):
    return templates.TemplateResponse("reports.html", {"request": request})
