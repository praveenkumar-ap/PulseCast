from __future__ import annotations

import time
import logging
from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from .context import get_request_context
from .config import settings

logger = logging.getLogger("pulsecast_api.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log one line per HTTP request."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request/response metadata once per request."""
        start = time.time()
        ctx = None
        try:
            ctx = await get_request_context(request)
        except Exception:
            # health and unauthenticated routes may still proceed; context may be None
            ctx = None

        response: Response | None = None
        try:
            response = await call_next(request)
            return response
        finally:
            duration_ms = int((time.time() - start) * 1000)
            status_code = getattr(response, "status_code", None) if response is not None else 500
            logger.info(
                "method=%s path=%s status=%s duration_ms=%s env=%s user_id=%s tenant_id=%s",
                request.method,
                request.url.path,
                status_code,
                duration_ms,
                settings.environment,
                getattr(ctx, "user_id", None),
                getattr(ctx, "tenant_id", None),
            )
