"""
Analysis trigger and results API endpoints
Runs the full LangGraph multi-agent pipeline
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from backend.db.database import get_db
from backend.models.resume import Resume, ResumeStatus
from backend.models.job import Job
from backend.models.user import User
from backend.schemas.schemas import AnalysisRequest, AnalysisResult
from backend.api.auth import get_current_user
from backend.services.orchestrator import run_full_analysis_pipeline

router = APIRouter()


@router.post("/run", summary="Run full AI analysis pipeline")
async def run_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Trigger the full multi-agent analysis pipeline:
    - Resume parsing → JD analysis → Semantic matching
    - ATS scoring → Skill gap → STAR rewrite → Interview Q gen
    - Report generation
    """
    # Validate resume
    result = await db.execute(select(Resume).where(Resume.id == request.resume_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if resume.status != ResumeStatus.processed:
        raise HTTPException(status_code=400, detail=f"Resume not ready (status: {resume.status})")

    # Validate job
    result = await db.execute(select(Job).where(Job.id == request.job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    background_tasks.add_task(run_full_analysis_pipeline, request.resume_id, request.job_id, db)

    return {
        "status": "started",
        "message": "Analysis pipeline running in background",
        "resume_id": request.resume_id,
        "job_id": request.job_id,
    }


@router.get("/result/{resume_id}/{job_id}", summary="Get analysis results")
async def get_analysis_result(
    resume_id: str,
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve the cached analysis results for a resume-job pair."""
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    if resume.ats_score is None:
        return {"status": "pending", "message": "Analysis not yet complete"}

    return {
        "status": "complete",
        "resume_id": resume_id,
        "job_id": job_id,
        "ats_score": resume.ats_score,
        "ats_breakdown": resume.ats_breakdown,
        "skill_gaps": resume.skill_gaps,
        "rewritten_bullets": resume.rewritten_bullets,
        "interview_questions": resume.interview_questions,
        "report_path": resume.report_path,
    }


@router.get("/recruiter/compare", summary="Recruiter: compare multiple candidates")
async def compare_candidates(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Recruiter view: compare all candidates who applied/analyzed for a specific job.
    Returns ranked list with ATS scores and key metrics.
    """
    if current_user.role != "recruiter":
        raise HTTPException(status_code=403, detail="Recruiter access required")

    # Get all resumes with ATS scores (analyzed)
    result = await db.execute(
        select(Resume).where(Resume.ats_score.isnot(None)).order_by(Resume.ats_score.desc())
    )
    resumes = result.scalars().all()

    candidates = []
    for r in resumes:
        parsed = r.parsed_data or {}
        candidates.append({
            "resume_id": r.id,
            "candidate_name": parsed.get("name", "Unknown"),
            "email": parsed.get("email", ""),
            "ats_score": r.ats_score,
            "ats_breakdown": r.ats_breakdown,
            "top_skills": (parsed.get("skills", []) or [])[:5],
            "status": r.status,
            "filename": r.filename,
        })

    return {
        "job_id": job_id,
        "total_candidates": len(candidates),
        "candidates": candidates,
    }
