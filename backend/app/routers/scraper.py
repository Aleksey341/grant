from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime
import logging

from app.database import get_db
from app.models.grant import Grant, GrantDeadline, GrantSnapshot
from app.dependencies import get_admin_user
from app.models.user import User
from app.services import scraper_service

router = APIRouter(prefix="/api/scrape", tags=["scraper"])
logger = logging.getLogger(__name__)

_scrape_status = {"running": False, "last_run": None, "results": []}


async def _run_scrape(db_session_factory):
    _scrape_status["running"] = True
    _scrape_status["results"] = []
    try:
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Grant).where(Grant.is_active == True))
            grants = result.scalars().all()
            for grant in grants:
                if not grant.source_url:
                    continue
                try:
                    data = await scraper_service.scrape_grant(grant.id, grant.source_url, grant.source_name)
                    snapshot = GrantSnapshot(
                        grant_id=grant.id,
                        raw_html=data.get("raw_text_preview", ""),
                        extracted_json=data.get("extracted", {}),
                        changes_detected=data.get("extracted", {}).get("changes_detected", False),
                    )
                    db.add(snapshot)
                    grant.last_scraped_at = datetime.utcnow()

                    # Update deadlines from AI extraction
                    extracted = data.get("extracted", {})
                    if "deadlines" in extracted:
                        for dl in extracted["deadlines"]:
                            if dl.get("date") and dl["date"] != "null":
                                try:
                                    dl_date = datetime.fromisoformat(dl["date"])
                                    deadline = GrantDeadline(
                                        grant_id=grant.id,
                                        deadline_date=dl_date,
                                        window_label=dl.get("label", ""),
                                        is_confirmed=dl.get("is_confirmed", False),
                                        source="ai_scraped",
                                    )
                                    db.add(deadline)
                                except Exception:
                                    pass

                    _scrape_status["results"].append({"grant": grant.source_name, "success": True})
                except Exception as e:
                    logger.error(f"Scrape error for {grant.source_name}: {e}")
                    _scrape_status["results"].append({"grant": grant.source_name, "success": False, "error": str(e)})

            await db.commit()
    finally:
        _scrape_status["running"] = False
        _scrape_status["last_run"] = datetime.utcnow().isoformat()


@router.post("/run")
async def run_scrape(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_admin_user),
):
    if _scrape_status["running"]:
        return {"message": "Scraping already in progress", "status": _scrape_status}
    background_tasks.add_task(_run_scrape, None)
    return {"message": "Scraping started", "status": _scrape_status}


@router.get("/status")
async def scrape_status(current_user: User = Depends(get_admin_user)):
    return _scrape_status
