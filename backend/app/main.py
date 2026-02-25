from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.database import init_db
from app.config import settings
from app.routers import auth, grants, applications, ai, documents, notifications, scraper, admin
from app.services.scheduler_service import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting GrantsAssistant API...")
    await init_db()
    start_scheduler()
    yield
    # Shutdown
    stop_scheduler()
    logger.info("GrantsAssistant API stopped")


app = FastAPI(
    title="GrantsAssistant API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(grants.router)
app.include_router(applications.router)
app.include_router(ai.router)
app.include_router(documents.router)
app.include_router(notifications.router)
app.include_router(scraper.router)
app.include_router(admin.router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0", "environment": settings.environment}


@app.get("/")
async def root():
    return {"message": "GrantsAssistant API", "docs": "/docs"}
