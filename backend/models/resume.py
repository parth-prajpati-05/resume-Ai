"""
SQLAlchemy Resume model
"""

from sqlalchemy import Column, String, Float, JSON, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from backend.db.database import Base


class ResumeStatus(str, enum.Enum):
    uploaded = "uploaded"
    processing = "processing"
    processed = "processed"
    failed = "failed"


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # pdf, docx, image

    # Parsed data
    parsed_data = Column(JSON, nullable=True)  # Full structured resume JSON
    raw_text = Column(Text, nullable=True)
    embedding_id = Column(String, nullable=True)  # ChromaDB document ID

    # Status
    status = Column(Enum(ResumeStatus), default=ResumeStatus.uploaded)
    error_message = Column(Text, nullable=True)

    # Analysis results (cached)
    ats_score = Column(Float, nullable=True)
    ats_breakdown = Column(JSON, nullable=True)
    skill_gaps = Column(JSON, nullable=True)
    rewritten_bullets = Column(JSON, nullable=True)
    interview_questions = Column(JSON, nullable=True)
    report_path = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="resumes")

    def __repr__(self):
        return f"<Resume {self.filename} ({self.status})>"
