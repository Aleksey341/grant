from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime


class GrantDeadlineOut(BaseModel):
    id: int
    deadline_date: Optional[datetime]
    window_label: Optional[str]
    is_confirmed: bool
    source: str

    model_config = {"from_attributes": True}


class GrantBase(BaseModel):
    source_name: str
    source_url: Optional[str] = None
    who_can_apply: Optional[str] = None
    age_restrictions: Optional[str] = None
    max_amount: Optional[int] = None
    max_amount_text: Optional[str] = None
    window_schedule: Optional[str] = None
    typical_docs: Optional[str] = None
    reporting: Optional[str] = None
    critical_notes: Optional[str] = None
    submission_target: Optional[str] = None
    category: str = "individual"
    is_active: bool = True


class GrantCreate(GrantBase):
    pass


class GrantUpdate(BaseModel):
    source_name: Optional[str] = None
    source_url: Optional[str] = None
    who_can_apply: Optional[str] = None
    age_restrictions: Optional[str] = None
    max_amount: Optional[int] = None
    max_amount_text: Optional[str] = None
    window_schedule: Optional[str] = None
    typical_docs: Optional[str] = None
    reporting: Optional[str] = None
    critical_notes: Optional[str] = None
    submission_target: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None


class GrantOut(GrantBase):
    id: int
    last_scraped_at: Optional[datetime]
    created_at: datetime
    deadlines: List[GrantDeadlineOut] = []

    model_config = {"from_attributes": True}


class GrantListOut(BaseModel):
    id: int
    source_name: str
    source_url: Optional[str]
    max_amount: Optional[int]
    max_amount_text: Optional[str]
    category: str
    is_active: bool
    nearest_deadline: Optional[datetime] = None
    deadline_label: Optional[str] = None

    model_config = {"from_attributes": True}


class GrantFilters(BaseModel):
    category: Optional[str] = None
    max_amount_min: Optional[int] = None
    max_amount_max: Optional[int] = None
    days_until_deadline: Optional[int] = None
    search: Optional[str] = None
