import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.database import get_db
from app.models.user import User
from app.schemas.user import PushSubscriptionIn, TelegramConnectIn
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.post("/push/subscribe")
async def subscribe_push(
    data: PushSubscriptionIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.push_endpoint = data.endpoint
    current_user.push_p256dh = data.p256dh
    current_user.push_auth = data.auth
    current_user.notify_push = True
    await db.commit()
    return {"message": "Push subscription saved"}


@router.post("/push/unsubscribe")
async def unsubscribe_push(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.push_endpoint = None
    current_user.push_p256dh = None
    current_user.push_auth = None
    current_user.notify_push = False
    await db.commit()
    return {"message": "Push unsubscribed"}


@router.get("/telegram/link-code")
async def get_telegram_link_code(current_user: User = Depends(get_current_user)):
    return {
        "link_code": current_user.telegram_link_code,
        "bot_url": "https://t.me/your_bot_username",
        "instruction": f"Отправьте боту команду: /link {current_user.telegram_link_code}",
    }


@router.post("/telegram/connect")
async def connect_telegram(
    data: TelegramConnectIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # This is called by the Telegram bot after user sends /link code
    result = await db.execute(
        select(User).where(User.telegram_link_code == data.link_code)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid link code")

    # In real bot, telegram would provide chat_id. Here we just mark as connected.
    user.notify_telegram = True
    await db.commit()
    return {"message": "Telegram connected successfully"}


@router.get("/vapid-public-key")
async def get_vapid_public_key():
    from app.config import settings
    return {"public_key": settings.vapid_public_key or ""}
