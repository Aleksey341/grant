from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class ApplicationCreate(BaseModel):
    grant_id: int


class ApplicationUpdate(BaseModel):
    current_step: Optional[int] = None
    wizard_data: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class ApplicationOut(BaseModel):
    id: int
    grant_id: int
    user_id: int
    status: str
    current_step: int
    wizard_data: Dict[str, Any]
    ai_hints: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class AIHintRequest(BaseModel):
    application_id: int
    field_name: str
    current_value: str
    grant_id: int


class AICheckTextRequest(BaseModel):
    text: str
    context: Optional[str] = None


class AIGenerateSectionRequest(BaseModel):
    section_name: str
    project_topic: str
    target_audience: str
    applicant_data: Dict[str, Any]
    grant_id: int


class DocumentRequest(BaseModel):
    application_id: int
