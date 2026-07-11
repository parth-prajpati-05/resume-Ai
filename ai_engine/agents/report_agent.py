"""
Report Agent — triggers PDF report generation
"""

from typing import Dict
from loguru import logger


class ReportAgent:
    """Orchestrates PDF report generation."""

    def __init__(self):
        from ai_engine.report.pdf_generator import PDFReportGenerator
        self.generator = PDFReportGenerator()

    async def run(
        self,
        resume_data: dict,
        ats_score: float,
        ats_breakdown: dict,
        skill_gaps: dict,
        rewritten_bullets: list,
        interview_questions: list,
        resume_id: str,
        job_id: str,
    ) -> str:
        """Generate PDF report and return file path."""
        logger.info(f"[ReportAgent] Generating PDF for resume {resume_id}")
        path = await self.generator.generate(
            resume_data=resume_data,
            ats_score=ats_score,
            ats_breakdown=ats_breakdown,
            skill_gaps=skill_gaps,
            rewritten_bullets=rewritten_bullets,
            interview_questions=interview_questions,
            resume_id=resume_id,
            job_id=job_id,
        )
        logger.info(f"[ReportAgent] Report saved to {path}")
        return path
