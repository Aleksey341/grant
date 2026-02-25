from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    grant_id = Column(Integer, ForeignKey("grants.id"), nullable=False)
    status = Column(String(50), default="draft")  # draft/in_progress/complete
    current_step = Column(Integer, default=1)
    wizard_data = Column(JSON, default=dict)
    ai_hints = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="applications")
    grant = relationship("Grant", back_populates="applications")
    documents = relationship("GeneratedDocument", back_populates="application", cascade="all, delete-orphan")


class GeneratedDocument(Base):
    __tablename__ = "generated_documents"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    doc_type = Column(String(10), nullable=False)  # pdf/docx
    file_path = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    application = relationship("Application", back_populates="documents")
