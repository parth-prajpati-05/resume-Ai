"""
Tests for FastAPI API endpoints
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from backend.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.asyncio
class TestAuthAPI:
    """Tests for authentication endpoints."""

    async def test_register_candidate(self):
        async with AsyncClient(app=app, base_url="http://test") as client:
            resp = await client.post("/api/auth/register", json={
                "email": "test_candidate@example.com",
                "username": "testcandidate",
                "password": "testpass123",
                "role": "candidate",
            })
            assert resp.status_code in [201, 400]  # 400 if already exists

    async def test_login_invalid_credentials(self):
        async with AsyncClient(app=app, base_url="http://test") as client:
            resp = await client.post(
                "/api/auth/login",
                data={"username": "fake@example.com", "password": "wrongpass"},
            )
            assert resp.status_code == 401

    async def test_get_me_unauthorized(self):
        async with AsyncClient(app=app, base_url="http://test") as client:
            resp = await client.get("/api/auth/me")
            assert resp.status_code == 401


@pytest.mark.asyncio
class TestHealthAPI:
    """Tests for health and root endpoints."""

    async def test_root(self):
        async with AsyncClient(app=app, base_url="http://test") as client:
            resp = await client.get("/")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "running"

    async def test_health(self):
        async with AsyncClient(app=app, base_url="http://test") as client:
            resp = await client.get("/health")
            assert resp.status_code == 200
            assert resp.json()["status"] == "healthy"


@pytest.mark.asyncio
class TestResumeAPI:
    """Tests for resume endpoints (require auth)."""

    async def test_list_resumes_unauthorized(self):
        async with AsyncClient(app=app, base_url="http://test") as client:
            resp = await client.get("/api/resume/")
            assert resp.status_code == 401

    async def test_get_nonexistent_resume(self):
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Without auth token
            resp = await client.get("/api/resume/nonexistent-id")
            assert resp.status_code == 401
