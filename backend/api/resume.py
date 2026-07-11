"""
Resume upload and management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid
import os
import aiofiles

from backend.db.database import get_db
from backend.models.resume import Resume, ResumeStatus
from backend.models.user import User
from backend.schemas.schemas import ResumeOut, ParsedResume
from backend.api.auth import get_current_user
from backend.services.orchestrator import run_parsing_pipeline
from backend.core.config import settings

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".png", ".jpg", ".jpeg", ".tiff"}


async def save_upload(file: UploadFile, upload_dir: str) -> tuple[str, str]:
    """Save uploaded file and return (file_path, file_type)."""
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    unique_name = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(upload_dir, unique_name)

    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    return file_path, ext.lstrip(".")


@router.post("/upload", response_model=ResumeOut, status_code=201, summary="Upload a resume")
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a resume (PDF, DOCX, or image). Parsing runs asynchronously in the background.
    Supported formats: PDF, DOCX, DOC, PNG, JPG, JPEG, TIFF
    """
    file_path, file_type = await save_upload(file, settings.UPLOAD_DIR)

    resume = Resume(
        user_id=current_user.id,
        filename=file.filename,
        file_path=file_path,
        file_type=file_type,
        status=ResumeStatus.processing,
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)

    # Background parsing
    background_tasks.add_task(run_parsing_pipeline, resume.id, file_path, file_type)

    return resume


@router.get("/", response_model=List[ResumeOut], summary="List my resumes")
async def list_resumes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all resumes belonging to the current user."""
    result = await db.execute(
        select(Resume).where(Resume.user_id == current_user.id).order_by(Resume.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{resume_id}", response_model=ResumeOut, summary="Get resume by ID")
async def get_resume(
    resume_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get details of a specific resume."""
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if resume.user_id != current_user.id and current_user.role != "recruiter":
        raise HTTPException(status_code=403, detail="Access denied")
    return resume


@router.get("/{resume_id}/parsed", response_model=ParsedResume, summary="Get parsed resume data")
async def get_parsed_resume(
    resume_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the structured parsed data of a resume."""
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if resume.status != ResumeStatus.processed:
        raise HTTPException(status_code=400, detail=f"Resume is still {resume.status}")
    return resume.parsed_data or {}


@router.delete("/{resume_id}", status_code=204, summary="Delete a resume")
async def delete_resume(
    resume_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a resume and its associated file."""
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if resume.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Remove file
    if os.path.exists(resume.file_path):
        os.remove(resume.file_path)

    await db.delete(resume)
    await db.commit()
