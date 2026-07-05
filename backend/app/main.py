import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from app.config import settings, STATIC_DIR
from app.database import engine, Base
from app.routers import auth, categories, items, detection, dashboard, reports
from app.jinja_setup import templates

Base.metadata.create_all(bind=engine)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="Detect App")

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(items.router)
app.include_router(detection.router)
app.include_router(dashboard.router)
app.include_router(reports.router)

@app.get("/")
async def root():
    return RedirectResponse(url="/dashboard")
