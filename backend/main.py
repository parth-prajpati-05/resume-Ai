"""
AI Resume Intelligence Platform - FastAPI Backend
Main application entry point with full API documentation
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from contextlib import asynccontextmanager
from loguru import logger
import sys

from backend.db.database import init_db
from backend.api import auth, resume, jobs, analysis, reports
from backend.middleware.logging_middleware import LoggingMiddleware
from backend.core.config import settings


# ── Configure Loguru ──────────────────────────────────────────────────────────
logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan> - <white>{message}</white>",
    level="INFO",
)
logger.add("logs/app.log", rotation="10 MB", retention="7 days", level="DEBUG")


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting AI Resume Intelligence Platform...")
    await init_db()
    logger.info("✅ Database initialized")
    yield
    logger.info("🛑 Shutting down...")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AI Resume Intelligence Platform",
    description="""
## 🤖 AI-Powered Resume Analysis Platform

A production-ready platform for intelligent resume analysis, ATS scoring,
skill gap detection, and personalized interview preparation.

### Features
- **RAG-powered semantic matching** — resume ↔ job description
- **OCR support** — scan image/PDF resumes
- **ATS Scoring** — explainable breakdown with weights
- **STAR Resume Rewriting** — AI-powered improvement suggestions
- **Skill Gap Analysis** — with learning recommendations
- **Interview Question Generation** — personalized Q&A sets
- **PDF Report Generation** — downloadable professional reports
- **Multi-role Auth** — Recruiter and Candidate roles

### Authentication
Use `/api/auth/login` to get a JWT token, then use `Bearer <token>` in headers.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ── Middleware ────────────────────────────────────────────────────────────────
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(resume.router, prefix="/api/resume", tags=["Resume"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Job Descriptions"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])


# ── Health & Root ─────────────────────────────────────────────────────────────
@app.get("/", tags=["Root"])
async def root():
    return {
        "app": "AI Resume Intelligence Platform",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Root"])
async def health_check():
    return {"status": "healthy", "service": "resume-ai-backend"}
