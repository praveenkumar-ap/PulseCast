import logging
from datetime import datetime
import hashlib
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from .core.context import get_request_context
from .core.db import SessionLocal, get_db
from .core.logging_config import configure_logging
from .core.middleware import RequestLoggingMiddleware
from .models.audit import APIAuditLog
from .routers import alerts, forecasts, scenarios, optimizer, indicators, metrics, explain, signals, value, health as health_router


class AuditMiddleware(BaseHTTPMiddleware):
    """Capture API audit events."""

    async def dispatch(self, request: Request, call_next):
        start = datetime.utcnow()
        ctx = None
        try:
            ctx = await get_request_context(request)
        except HTTPException:
            # will be handled downstream; still attempt to log with minimal context
            ctx = None

        body_bytes = await request.body()
        payload_hash = hashlib.sha256(body_bytes).hexdigest() if body_bytes else None

        response: Response
        try:
            response = await call_next(request)
        except Exception:
            response = Response(status_code=500)
            raise
        finally:
            try:
                session = SessionLocal()
                audit = APIAuditLog(
                    id=uuid4(),
                    tenant_id=ctx.tenant_id if ctx else None,
                    user_id=ctx.user_id if ctx else None,
                    user_role=ctx.user_role if ctx else None,
                    path=request.url.path,
                    method=request.method,
                    status_code=response.status_code,
                    timestamp=start,
                    action=None,
                    entity_type=None,
                    entity_id=None,
                    payload_hash=payload_hash,
                )
                session.add(audit)
                session.commit()
            except Exception as exc:  # noqa: BLE001
                logging.getLogger(__name__).error("Failed to write audit log", exc_info=exc)
            finally:
                try:
                    session.close()
                except Exception:
                    pass
        return response


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="pulsecast_api")
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(AuditMiddleware)

    app.include_router(forecasts.router)
    app.include_router(alerts.router)
    app.include_router(scenarios.router)
    app.include_router(optimizer.router)
    app.include_router(indicators.router)
    app.include_router(metrics.router)
    app.include_router(explain.router)
    app.include_router(signals.router)
    app.include_router(value.router)
    app.include_router(health_router.router)
    return app


app = create_app()
