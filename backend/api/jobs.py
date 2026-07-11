"""
Job Description management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from backend.db.database import get_db
from backend.models.job import Job, JobStatus
from backend.models.user import User
from backend.schemas.schemas import JobCreate, JobOut
from backend.api.auth import get_current_user
from backend.services.orchestrator import run_jd_parsing_pipeline

router = APIRouter()


@router.post("/", response_model=JobOut, status_code=201, summary="Create a job description")
async def create_job(
    job_data: JobCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new job description. Recruiters can create JDs for matching."""
    job = Job(
        user_id=current_user.id,
        title=job_data.title,
        company=job_data.company,
        description=job_data.description,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Parse JD in background
    await run_jd_parsing_pipeline(job.id, job_data.description, db)

    return job


@router.get("/", response_model=List[JobOut], summary="List job descriptions")
async def list_jobs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all available job descriptions."""
    if current_user.role == "recruiter":
        result = await db.execute(
            select(Job).where(Job.user_id == current_user.id).order_by(Job.created_at.desc())
        )
    else:
        # Candidates see all active jobs
        result = await db.execute(
            select(Job).where(Job.status == JobStatus.active).order_by(Job.created_at.desc())
        )
    return result.scalars().all()


@router.get("/{job_id}", summary="Get job description details")
async def get_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get full details of a specific job description."""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "description": job.description,
        "required_skills": job.required_skills or [],
        "parsed_data": job.parsed_data or {},
        "status": job.status,
        "created_at": job.created_at,
    }


@router.delete("/{job_id}", status_code=204, summary="Delete a job description")
async def delete_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a job description (recruiter only)."""
    if current_user.role != "recruiter":
        raise HTTPException(status_code=403, detail="Recruiter access required")
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    await db.delete(job)
    await db.commit()
