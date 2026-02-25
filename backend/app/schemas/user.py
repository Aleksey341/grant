from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    is_admin: bool
    notify_email: bool
    notify_telegram: bool
    notify_push: bool
    telegram_chat_id: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    notify_email: Optional[bool] = None
    notify_telegram: Optional[bool] = None
    notify_push: Optional[bool] = None


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class PushSubscriptionIn(BaseModel):
    endpoint: str
    p256dh: str
    auth: str


class TelegramConnectIn(BaseModel):
    link_code: str
