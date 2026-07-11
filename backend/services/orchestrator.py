"""
Service Orchestrator — coordinates AI engine agents
Called by API endpoints to run the multi-agent pipeline
"""

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


async def run_parsing_pipeline(resume_id: str, file_path: str, file_type: str):
    """Background task: Parse uploaded resume and store in DB + ChromaDB."""
    try:
        from backend.db.database import AsyncSessionLocal
        from backend.models.resume import Resume, ResumeStatus
        from ai_engine.orchestrator.langgraph_flow import ResumeIntelligenceFlow

        logger.info(f"📄 Starting parsing pipeline for resume {resume_id}")
        
        flow = ResumeIntelligenceFlow()
        parsed = await flow.parse_resume(file_path, file_type)

        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Resume).where(Resume.id == resume_id))
            resume = result.scalar_one_or_none()
            if resume:
                resume.parsed_data = parsed
                resume.raw_text = parsed.get("raw_text", "")
                resume.status = ResumeStatus.processed
                resume.embedding_id = await flow.embed_and_store(resume_id, parsed)
                await db.commit()
                logger.info(f"✅ Resume {resume_id} parsed and embedded")

    except Exception as e:
        logger.error(f"❌ Parsing pipeline failed for {resume_id}: {e}")
        from backend.db.database import AsyncSessionLocal
        from backend.models.resume import Resume, ResumeStatus
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Resume).where(Resume.id == resume_id))
            resume = result.scalar_one_or_none()
            if resume:
                resume.status = ResumeStatus.failed
                resume.error_message = str(e)
                await db.commit()


async def run_jd_parsing_pipeline(job_id: str, description: str, db: AsyncSession):
    """Parse a job description and extract structured data + skills."""
    try:
        from backend.models.job import Job
        from ai_engine.orchestrator.langgraph_flow import ResumeIntelligenceFlow

        flow = ResumeIntelligenceFlow()
        parsed_jd = await flow.parse_jd(description)

        result = await db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        if job:
            job.parsed_data = parsed_jd
            job.required_skills = parsed_jd.get("required_skills", [])
            await db.commit()
            logger.info(f"✅ JD {job_id} parsed successfully")

    except Exception as e:
        logger.error(f"❌ JD parsing failed for {job_id}: {e}")


async def run_full_analysis_pipeline(resume_id: str, job_id: str, db: AsyncSession):
    """
    Full multi-agent pipeline:
    Retrieve → Score → Skill Gap → Rewrite → Interview → Report
    """
    try:
        from backend.models.resume import Resume
        from backend.models.job import Job
        from ai_engine.orchestrator.langgraph_flow import ResumeIntelligenceFlow

        logger.info(f"🔄 Running full analysis: resume={resume_id}, job={job_id}")

        res_result = await db.execute(select(Resume).where(Resume.id == resume_id))
        resume = res_result.scalar_one_or_none()

        job_result = await db.execute(select(Job).where(Job.id == job_id))
        job = job_result.scalar_one_or_none()

        if not resume or not job:
            logger.error("Resume or job not found for analysis")
            return

        flow = ResumeIntelligenceFlow()
        results = await flow.run_full_pipeline(
            resume_data=resume.parsed_data,
            jd_data=job.parsed_data,
            resume_text=resume.raw_text or "",
            jd_text=job.description,
        )

        # Store results
        resume.ats_score = results.get("ats_score", 0.0)
        resume.ats_breakdown = results.get("ats_breakdown", {})
        resume.skill_gaps = results.get("skill_gaps", {})
        resume.rewritten_bullets = results.get("rewritten_bullets", [])
        resume.interview_questions = results.get("interview_questions", [])
        await db.commit()

        logger.info(f"✅ Full analysis complete for resume {resume_id} — ATS: {resume.ats_score:.1f}")

    except Exception as e:
        logger.error(f"❌ Full analysis pipeline failed: {e}")


async def generate_pdf_report(resume, job_id: str) -> str:
    """Generate a PDF report for the resume-job analysis."""
    from ai_engine.report.pdf_generator import PDFReportGenerator

    generator = PDFReportGenerator()
    report_path = await generator.generate(
        resume_data=resume.parsed_data or {},
        ats_score=resume.ats_score or 0.0,
        ats_breakdown=resume.ats_breakdown or {},
        skill_gaps=resume.skill_gaps or {},
        rewritten_bullets=resume.rewritten_bullets or [],
        interview_questions=resume.interview_questions or [],
        resume_id=resume.id,
        job_id=job_id,
    )
    return report_path
