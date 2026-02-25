import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def check_deadlines():
    """Daily job: check deadlines and send reminders."""
    from app.database import AsyncSessionLocal
    from sqlalchemy import select, and_
    from app.models.grant import Grant, GrantDeadline
    from app.models.notification import UserGrantSubscription, NotificationLog
    from app.models.user import User
    from app.services.notification_service import send_deadline_reminder

    reminder_days = [30, 14, 7, 1]
    now = datetime.utcnow()

    async with AsyncSessionLocal() as db:
        for days in reminder_days:
            target_date = now + timedelta(days=days)
            deadlines = await db.execute(
                select(GrantDeadline).where(
                    and_(
                        GrantDeadline.deadline_date >= target_date.replace(hour=0, minute=0, second=0),
                        GrantDeadline.deadline_date < target_date.replace(hour=23, minute=59, second=59),
                    )
                )
            )
            for deadline in deadlines.scalars().all():
                # Get subscribers
                subs = await db.execute(
                    select(UserGrantSubscription).where(
                        UserGrantSubscription.grant_id == deadline.grant_id
                    )
                )
                for sub in subs.scalars().all():
                    # Check if already sent
                    existing = await db.execute(
                        select(NotificationLog).where(
                            and_(
                                NotificationLog.user_id == sub.user_id,
                                NotificationLog.grant_id == deadline.grant_id,
                                NotificationLog.days_before == days,
                                NotificationLog.message_type == "deadline_reminder",
                            )
                        )
                    )
                    if existing.scalar_one_or_none():
                        continue

                    user_result = await db.execute(select(User).where(User.id == sub.user_id))
                    user = user_result.scalar_one_or_none()
                    grant_result = await db.execute(select(Grant).where(Grant.id == deadline.grant_id))
                    grant = grant_result.scalar_one_or_none()

                    if user and grant:
                        await send_deadline_reminder(user, grant, days, db)


async def weekly_scrape():
    """Weekly job: scrape all grant URLs."""
    from app.database import AsyncSessionLocal
    from sqlalchemy import select
    from app.models.grant import Grant, GrantDeadline, GrantSnapshot
    from app.services.scraper_service import scrape_grant

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Grant).where(Grant.is_active == True))
        grants = result.scalars().all()
        for grant in grants:
            if not grant.source_url:
                continue
            try:
                data = await scrape_grant(grant.id, grant.source_url, grant.source_name)
                snapshot = GrantSnapshot(
                    grant_id=grant.id,
                    raw_html=data.get("raw_text_preview", ""),
                    extracted_json=data.get("extracted", {}),
                )
                db.add(snapshot)
                grant.last_scraped_at = datetime.utcnow()
            except Exception as e:
                logger.error(f"Weekly scrape error for {grant.source_name}: {e}")
        await db.commit()
    logger.info("Weekly scrape completed")


def start_scheduler():
    if scheduler.running:
        return
    scheduler.add_job(check_deadlines, CronTrigger(hour=9, minute=0), id="check_deadlines", replace_existing=True)
    scheduler.add_job(weekly_scrape, CronTrigger(day_of_week="mon", hour=2, minute=0), id="weekly_scrape", replace_existing=True)
    scheduler.start()
    logger.info("Scheduler started")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
