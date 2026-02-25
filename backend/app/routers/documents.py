import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.application import Application, GeneratedDocument
from app.models.grant import Grant
from app.dependencies import get_current_user
from app.models.user import User
from app.services import document_service

router = APIRouter(prefix="/api/documents", tags=["documents"])
DOCS_DIR = "generated_docs"
os.makedirs(DOCS_DIR, exist_ok=True)


@router.post("/pdf/{app_id}")
async def generate_pdf(
    app_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    app_result = await db.execute(
        select(Application).where(Application.id == app_id, Application.user_id == current_user.id)
    )
    app = app_result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    grant_result = await db.execute(select(Grant).where(Grant.id == app.grant_id))
    grant = grant_result.scalar_one_or_none()

    output_path = os.path.join(DOCS_DIR, f"app_{app_id}.pdf")
    await document_service.generate_pdf(
        {"wizard_data": app.wizard_data},
        {"source_name": grant.source_name if grant else ""},
        output_path,
    )

    doc = GeneratedDocument(application_id=app_id, doc_type="pdf", file_path=output_path)
    db.add(doc)
    await db.commit()

    return {"download_url": f"/api/documents/download/{app_id}/pdf", "file_path": output_path}


@router.post("/docx/{app_id}")
async def generate_docx(
    app_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    app_result = await db.execute(
        select(Application).where(Application.id == app_id, Application.user_id == current_user.id)
    )
    app = app_result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    grant_result = await db.execute(select(Grant).where(Grant.id == app.grant_id))
    grant = grant_result.scalar_one_or_none()

    output_path = os.path.join(DOCS_DIR, f"app_{app_id}.docx")
    await document_service.generate_docx(
        {"wizard_data": app.wizard_data},
        {"source_name": grant.source_name if grant else ""},
        output_path,
    )

    doc = GeneratedDocument(application_id=app_id, doc_type="docx", file_path=output_path)
    db.add(doc)
    await db.commit()

    return {"download_url": f"/api/documents/download/{app_id}/docx"}


@router.get("/download/{app_id}/{doc_type}")
async def download_document(
    app_id: int,
    doc_type: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    app_result = await db.execute(
        select(Application).where(Application.id == app_id, Application.user_id == current_user.id)
    )
    if not app_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Application not found")

    doc_result = await db.execute(
        select(GeneratedDocument).where(
            GeneratedDocument.application_id == app_id,
            GeneratedDocument.doc_type == doc_type,
        ).order_by(GeneratedDocument.created_at.desc())
    )
    doc = doc_result.scalars().first()
    if not doc or not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="Document not found, generate it first")

    media_type = "application/pdf" if doc_type == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    filename = f"grant_application_{app_id}.{doc_type}"
    return FileResponse(doc.file_path, media_type=media_type, filename=filename)
