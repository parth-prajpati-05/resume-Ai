"""
Tests Configuration and Fixtures
"""

import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_resume_ai.db"


class Base(DeclarativeBase):
    pass


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
def sample_resume_text():
    return """
    John Doe
    john.doe@example.com | +1-555-123-4567 | San Francisco, CA
    LinkedIn: linkedin.com/in/johndoe | GitHub: github.com/johndoe

    SUMMARY
    Senior Python Engineer with 5+ years of experience building scalable backend systems.

    EXPERIENCE
    Senior Software Engineer — TechCorp Inc. (2021 - Present)
    - Architected microservices platform handling 1M+ daily requests using FastAPI and Docker
    - Reduced API latency by 45% through Redis caching and query optimization
    - Led team of 5 engineers to deliver features 30% ahead of schedule

    Software Engineer — StartupXYZ (2019 - 2021)
    - Built ML pipeline processing 500K data points daily using Python and TensorFlow
    - Implemented CI/CD using GitHub Actions, reducing deployment time by 60%

    EDUCATION
    B.S. Computer Science — Stanford University (2019)

    SKILLS
    Python, FastAPI, Docker, Kubernetes, PostgreSQL, Redis, TensorFlow, AWS, Git, REST API

    CERTIFICATIONS
    AWS Solutions Architect Associate (2022)
    """


@pytest.fixture
def sample_jd_text():
    return """
    Senior Python Engineer

    We are looking for a Senior Python Engineer to join our backend team.

    Requirements:
    - 4+ years of Python experience
    - Experience with FastAPI or Django
    - Proficiency in Docker and Kubernetes
    - Strong SQL and PostgreSQL skills
    - Experience with AWS or GCP
    - Knowledge of microservices architecture
    - CI/CD experience

    Nice to have:
    - Machine Learning experience
    - LangChain or LLM integration
    - Redis experience
    """


@pytest.fixture
def sample_resume_data():
    return {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1-555-123-4567",
        "location": "San Francisco, CA",
        "skills": ["Python", "FastAPI", "Docker", "Kubernetes", "PostgreSQL", "Redis", "TensorFlow", "AWS"],
        "experience": [
            {
                "company": "TechCorp Inc.",
                "role": "Senior Software Engineer",
                "duration": "2021 - Present",
                "bullets": [
                    "Architected microservices platform handling 1M+ daily requests",
                    "Reduced API latency by 45% through Redis caching",
                ]
            }
        ],
        "education": [
            {"institution": "Stanford University", "degree": "B.S.", "field": "Computer Science", "year": "2019"}
        ],
        "certifications": [
            {"name": "AWS Solutions Architect Associate", "issuer": "Amazon", "year": "2022"}
        ],
    }


@pytest.fixture
def sample_jd_data():
    return {
        "job_title": "Senior Python Engineer",
        "required_skills": ["Python", "FastAPI", "Docker", "Kubernetes", "PostgreSQL", "AWS"],
        "preferred_skills": ["Machine Learning", "LangChain", "Redis"],
        "experience_required": "4+ years",
        "education_required": "Bachelor's degree",
    }
