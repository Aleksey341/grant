from sqlalchemy import Column, Integer, String, BigInteger, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Grant(Base):
    __tablename__ = "grants"

    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String(500), nullable=False)
    source_url = Column(Text)
    who_can_apply = Column(Text)
    age_restrictions = Column(Text)
    max_amount = Column(BigInteger)
    max_amount_text = Column(String(500))
    window_schedule = Column(Text)
    typical_docs = Column(Text)
    reporting = Column(Text)
    critical_notes = Column(Text)
    submission_target = Column(String(500))
    category = Column(String(50), default="individual")  # individual/nko/business
    is_active = Column(Boolean, default=True)
    last_scraped_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    deadlines = relationship("GrantDeadline", back_populates="grant", cascade="all, delete-orphan")
    snapshots = relationship("GrantSnapshot", back_populates="grant", cascade="all, delete-orphan")
    subscriptions = relationship("UserGrantSubscription", back_populates="grant", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="grant")


class GrantDeadline(Base):
    __tablename__ = "grant_deadlines"

    id = Column(Integer, primary_key=True, index=True)
    grant_id = Column(Integer, ForeignKey("grants.id"), nullable=False)
    deadline_date = Column(DateTime(timezone=True))
    window_label = Column(String(200))
    is_confirmed = Column(Boolean, default=False)
    source = Column(String(100), default="manual")  # manual/scraped/ai
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    grant = relationship("Grant", back_populates="deadlines")


class GrantSnapshot(Base):
    __tablename__ = "grant_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    grant_id = Column(Integer, ForeignKey("grants.id"), nullable=False)
    raw_html = Column(Text)
    extracted_json = Column(JSON)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    changes_detected = Column(Boolean, default=False)

    grant = relationship("Grant", back_populates="snapshots")
