from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime, timedelta

from app.database import get_db
from app.models.grant import Grant, GrantDeadline
from app.models.notification import UserGrantSubscription
from app.schemas.grant import GrantOut, GrantListOut, GrantCreate, GrantUpdate
from app.dependencies import get_current_user, get_optional_user
from app.models.user import User

router = APIRouter(prefix="/api/grants", tags=["grants"])


@router.get("", response_model=List[GrantListOut])
async def list_grants(
    category: Optional[str] = Query(None),
    max_amount_min: Optional[int] = Query(None),
    max_amount_max: Optional[int] = Query(None),
    days_until_deadline: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Grant).options(selectinload(Grant.deadlines)).where(Grant.is_active == True)

    if category:
        query = query.where(Grant.category == category)
    if max_amount_min:
        query = query.where(Grant.max_amount >= max_amount_min)
    if max_amount_max:
        query = query.where(Grant.max_amount <= max_amount_max)
    if search:
        query = query.where(
            or_(
                Grant.source_name.ilike(f"%{search}%"),
                Grant.who_can_apply.ilike(f"%{search}%"),
                Grant.critical_notes.ilike(f"%{search}%"),
            )
        )

    result = await db.execute(query)
    grants = result.scalars().all()

    output = []
    now = datetime.utcnow()
    for g in grants:
        nearest = None
        label = None
        for d in sorted(g.deadlines, key=lambda x: x.deadline_date or datetime.max):
            if d.deadline_date and d.deadline_date > now:
                nearest = d.deadline_date
                label = d.window_label
                break
        if days_until_deadline and nearest:
            if (nearest - now).days > days_until_deadline:
                continue
        output.append(GrantListOut(
            id=g.id,
            source_name=g.source_name,
            source_url=g.source_url,
            max_amount=g.max_amount,
            max_amount_text=g.max_amount_text,
            category=g.category,
            is_active=g.is_active,
            nearest_deadline=nearest,
            deadline_label=label,
        ))

    output.sort(key=lambda x: x.nearest_deadline or datetime.max)
    return output


@router.get("/upcoming", response_model=List[GrantListOut])
async def upcoming_grants(
    days: int = Query(30),
    db: AsyncSession = Depends(get_db),
):
    now = datetime.utcnow()
    deadline_cutoff = now + timedelta(days=days)

    deadline_q = await db.execute(
        select(GrantDeadline).where(
            and_(
                GrantDeadline.deadline_date > now,
                GrantDeadline.deadline_date <= deadline_cutoff,
            )
        ).options(selectinload(GrantDeadline.grant))
    )
    deadlines = deadline_q.scalars().all()

    seen_grants = {}
    for d in sorted(deadlines, key=lambda x: x.deadline_date):
        g = d.grant
        if g.id not in seen_grants:
            seen_grants[g.id] = GrantListOut(
                id=g.id,
                source_name=g.source_name,
                source_url=g.source_url,
                max_amount=g.max_amount,
                max_amount_text=g.max_amount_text,
                category=g.category,
                is_active=g.is_active,
                nearest_deadline=d.deadline_date,
                deadline_label=d.window_label,
            )
    return list(seen_grants.values())


@router.get("/{grant_id}", response_model=GrantOut)
async def get_grant(grant_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Grant).options(selectinload(Grant.deadlines)).where(Grant.id == grant_id)
    )
    grant = result.scalar_one_or_none()
    if not grant:
        raise HTTPException(status_code=404, detail="Grant not found")
    return grant


@router.post("/{grant_id}/subscribe")
async def subscribe_to_grant(
    grant_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Grant).where(Grant.id == grant_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Grant not found")

    existing = await db.execute(
        select(UserGrantSubscription).where(
            and_(
                UserGrantSubscription.user_id == current_user.id,
                UserGrantSubscription.grant_id == grant_id,
            )
        )
    )
    if existing.scalar_one_or_none():
        return {"message": "Already subscribed"}

    sub = UserGrantSubscription(user_id=current_user.id, grant_id=grant_id)
    db.add(sub)
    await db.commit()
    return {"message": "Subscribed successfully"}


@router.delete("/{grant_id}/subscribe")
async def unsubscribe_from_grant(
    grant_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(UserGrantSubscription).where(
            and_(
                UserGrantSubscription.user_id == current_user.id,
                UserGrantSubscription.grant_id == grant_id,
            )
        )
    )
    sub = result.scalar_one_or_none()
    if sub:
        await db.delete(sub)
        await db.commit()
    return {"message": "Unsubscribed"}
