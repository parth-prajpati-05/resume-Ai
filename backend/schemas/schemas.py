"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    recruiter = "recruiter"
    candidate = "candidate"


# ── Auth Schemas ──────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.candidate


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: str


class UserOut(BaseModel):
    id: str
    email: str
    username: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Resume Schemas ─────────────────────────────────────────────────────────────

class ResumeOut(BaseModel):
    id: str
    filename: str
    file_type: str
    status: str
    ats_score: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class ParsedResume(BaseModel):
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    location: Optional[str]
    summary: Optional[str]
    education: list = []
    experience: list = []
    projects: list = []
    skills: list = []
    certifications: list = []
    languages: list = []


# ── Job Schemas ────────────────────────────────────────────────────────────────

class JobCreate(BaseModel):
    title: str
    company: Optional[str] = None
    description: str


class JobOut(BaseModel):
    id: str
    title: str
    company: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Analysis Schemas ───────────────────────────────────────────────────────────

class AnalysisRequest(BaseModel):
    resume_id: str
    job_id: str


class ATSBreakdown(BaseModel):
    keyword_match: float
    semantic_similarity: float
    skills_coverage: float
    format_score: float
    experience_alignment: float
    total_score: float


class SkillGap(BaseModel):
    missing_skills: list
    present_skills: list
    recommendations: list


class AnalysisResult(BaseModel):
    resume_id: str
    job_id: str
    ats_score: float
    ats_breakdown: ATSBreakdown
    skill_gaps: SkillGap
    rewritten_bullets: list
    interview_questions: list
    semantic_match_score: float
    summary: str
