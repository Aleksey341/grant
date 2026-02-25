from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.grant import Grant
from app.models.user import User
from app.models.application import Application
from app.models.notification import NotificationLog
from app.schemas.grant import GrantCreate, GrantUpdate, GrantOut
from app.dependencies import get_admin_user

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    grants_count = await db.execute(select(func.count(Grant.id)))
    users_count = await db.execute(select(func.count(User.id)))
    apps_count = await db.execute(select(func.count(Application.id)))
    notifs_count = await db.execute(select(func.count(NotificationLog.id)))

    return {
        "grants": grants_count.scalar(),
        "users": users_count.scalar(),
        "applications": apps_count.scalar(),
        "notifications_sent": notifs_count.scalar(),
    }


@router.get("/users")
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    return [{"id": u.id, "email": u.email, "full_name": u.full_name, "is_admin": u.is_admin, "created_at": u.created_at} for u in users]


@router.post("/grants", response_model=GrantOut)
async def create_grant(
    data: GrantCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    grant = Grant(**data.model_dump())
    db.add(grant)
    await db.commit()
    await db.refresh(grant)
    return grant


@router.put("/grants/{grant_id}", response_model=GrantOut)
async def update_grant(
    grant_id: int,
    data: GrantUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Grant).options(selectinload(Grant.deadlines)).where(Grant.id == grant_id)
    )
    grant = result.scalar_one_or_none()
    if not grant:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Grant not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(grant, field, value)
    await db.commit()
    await db.refresh(grant)
    return grant
