"""
Logging middleware — logs every request with timing and status
"""

# pyrefly: ignore [missing-import]
from fastapi import Request
# pyrefly: ignore [missing-import]
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger
import time


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        method = request.method
        url = str(request.url)

        logger.info(f"→ {method} {url}")

        try:
            response = await call_next(request)
            elapsed = round((time.time() - start) * 1000, 2)
            logger.info(f"← {method} {url} [{response.status_code}] {elapsed}ms")
            return response
        except Exception as e:
            elapsed = round((time.time() - start) * 1000, 2)
            logger.error(f"✗ {method} {url} [ERROR] {elapsed}ms — {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"detail": f"Internal server error: {str(e)}"},
            )
