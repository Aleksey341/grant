from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    grant_id = Column(Integer, ForeignKey("grants.id"))
    channel = Column(String(20), nullable=False)  # email/telegram/push
    message_type = Column(String(50))  # deadline_reminder/grant_update/etc
    days_before = Column(Integer)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    success = Column(Boolean, default=True)
    error_message = Column(String(500))

    user = relationship("User", back_populates="notifications")


class UserGrantSubscription(Base):
    __tablename__ = "user_grant_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    grant_id = Column(Integer, ForeignKey("grants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="subscriptions")
    grant = relationship("Grant", back_populates="subscriptions")
