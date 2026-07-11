"""
Report download API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os

from backend.db.database import get_db
from backend.models.resume import Resume
from backend.models.user import User
from backend.api.auth import get_current_user
from backend.services.orchestrator import generate_pdf_report

router = APIRouter()


@router.get("/{resume_id}/download", summary="Download PDF analysis report")
async def download_report(
    resume_id: str,
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download the PDF analysis report for a resume-job pair."""
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Generate report if not exists
    if not resume.report_path or not os.path.exists(resume.report_path):
        report_path = await generate_pdf_report(resume, job_id)
        resume.report_path = report_path
        await db.commit()
    
    if not os.path.exists(resume.report_path):
        raise HTTPException(status_code=404, detail="Report file not found")

    return FileResponse(
        path=resume.report_path,
        media_type="application/pdf",
        filename=f"resume_analysis_{resume_id[:8]}.pdf",
        headers={"Content-Disposition": f"attachment; filename=resume_analysis_{resume_id[:8]}.pdf"},
    )


@router.post("/{resume_id}/generate", summary="Generate/regenerate PDF report")
async def generate_report(
    resume_id: str,
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Explicitly generate or regenerate a PDF analysis report."""
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if resume.ats_score is None:
        raise HTTPException(status_code=400, detail="Analysis not complete yet. Run analysis first.")

    report_path = await generate_pdf_report(resume, job_id)
    resume.report_path = report_path
    await db.commit()

    return {
        "status": "generated",
        "report_path": report_path,
        "download_url": f"/api/reports/{resume_id}/download?job_id={job_id}",
    }
