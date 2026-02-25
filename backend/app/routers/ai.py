from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.application import Application
from app.models.grant import Grant
from app.schemas.application import AIHintRequest, AICheckTextRequest, AIGenerateSectionRequest
from app.dependencies import get_current_user
from app.models.user import User
from app.services import ai_service

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/hint")
async def get_hint(
    data: AIHintRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Get application
    app_result = await db.execute(
        select(Application).where(
            Application.id == data.application_id,
            Application.user_id == current_user.id,
        )
    )
    app = app_result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    # Check cache
    cache_key = f"{data.field_name}:{hash(data.current_value)}"
    if app.ai_hints and cache_key in app.ai_hints:
        return {"hint": app.ai_hints[cache_key], "cached": True}

    # Get grant info
    grant_result = await db.execute(select(Grant).where(Grant.id == data.grant_id))
    grant = grant_result.scalar_one_or_none()
    grant_info = ""
    if grant:
        grant_info = f"Название: {grant.source_name}\nКто может подать: {grant.who_can_apply}\nВозраст: {grant.age_restrictions}\nМаксимальная сумма: {grant.max_amount_text}"

    hint = await ai_service.get_hint_for_field(
        field_name=data.field_name,
        current_value=data.current_value,
        grant_info=grant_info,
    )

    # Cache hint
    hints = dict(app.ai_hints or {})
    hints[cache_key] = hint
    app.ai_hints = hints
    await db.commit()

    return {"hint": hint, "cached": False}


@router.post("/check-text")
async def check_text(
    data: AICheckTextRequest,
    current_user: User = Depends(get_current_user),
):
    result = await ai_service.check_text(data.text, data.context or "")
    return result


@router.post("/generate-section")
async def generate_section(
    data: AIGenerateSectionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    grant_result = await db.execute(select(Grant).where(Grant.id == data.grant_id))
    grant = grant_result.scalar_one_or_none()
    grant_requirements = ""
    if grant:
        grant_requirements = f"{grant.who_can_apply or ''} {grant.typical_docs or ''}"

    text = await ai_service.generate_section(
        section_name=data.section_name,
        project_topic=data.project_topic,
        target_audience=data.target_audience,
        applicant_data=data.applicant_data,
        grant_requirements=grant_requirements,
    )
    return {"text": text}
