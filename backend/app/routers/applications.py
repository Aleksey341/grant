from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from app.database import get_db
from app.models.application import Application
from app.models.grant import Grant
from app.schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationOut
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.get("", response_model=List[ApplicationOut])
async def list_applications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Application)
        .where(Application.user_id == current_user.id)
        .order_by(Application.updated_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=ApplicationOut)
async def create_application(
    data: ApplicationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Grant).where(Grant.id == data.grant_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Grant not found")

    app = Application(
        user_id=current_user.id,
        grant_id=data.grant_id,
        wizard_data={},
        ai_hints={},
    )
    db.add(app)
    await db.commit()
    await db.refresh(app)
    return app


@router.get("/{app_id}", response_model=ApplicationOut)
async def get_application(
    app_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Application).where(
            Application.id == app_id,
            Application.user_id == current_user.id,
        )
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


@router.put("/{app_id}", response_model=ApplicationOut)
async def update_application(
    app_id: int,
    data: ApplicationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Application).where(
            Application.id == app_id,
            Application.user_id == current_user.id,
        )
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if data.current_step is not None:
        app.current_step = data.current_step
    if data.status is not None:
        app.status = data.status
    if data.wizard_data is not None:
        app.wizard_data = {**(app.wizard_data or {}), **data.wizard_data}

    await db.commit()
    await db.refresh(app)
    return app


@router.delete("/{app_id}")
async def delete_application(
    app_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Application).where(
            Application.id == app_id,
            Application.user_id == current_user.id,
        )
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    await db.delete(app)
    await db.commit()
    return {"message": "Deleted"}
