from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # Notification channels
    telegram_chat_id = Column(String(50))
    telegram_link_code = Column(String(20))  # temporary code for linking
    push_endpoint = Column(Text)
    push_p256dh = Column(Text)
    push_auth = Column(Text)

    # Notification preferences
    notify_email = Column(Boolean, default=True)
    notify_telegram = Column(Boolean, default=False)
    notify_push = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    subscriptions = relationship("UserGrantSubscription", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user")
    notifications = relationship("NotificationLog", back_populates="user")
