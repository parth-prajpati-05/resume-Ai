"""
SQLAlchemy Job Description model
"""

from sqlalchemy import Column, String, Text, JSON, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from backend.db.database import Base


class JobStatus(str, enum.Enum):
    active = "active"
    archived = "archived"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    company = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    parsed_data = Column(JSON, nullable=True)  # Structured JD JSON
    embedding_id = Column(String, nullable=True)
    required_skills = Column(JSON, nullable=True)  # List[str]
    status = Column(Enum(JobStatus), default=JobStatus.active)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="jobs")

    def __repr__(self):
        return f"<Job {self.title} @ {self.company}>"
