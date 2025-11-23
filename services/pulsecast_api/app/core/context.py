from __future__ import annotations

import logging
from typing import Optional

from fastapi import Depends, Header, HTTPException, Request
from pydantic import BaseModel

from .config import settings

logger = logging.getLogger(__name__)


class RequestContext(BaseModel):
    user_id: Optional[str]
    user_role: Optional[str]
    tenant_id: Optional[str]
    auth_mode: str


async def get_request_context(
    request: Request,
    x_user_id: Optional[str] = Header(default=None, alias="X-User-Id"),
    x_user_role: Optional[str] = Header(default=None, alias="X-User-Role"),
    x_tenant_id: Optional[str] = Header(default=None, alias="X-Tenant-Id"),
) -> RequestContext:
    """Resolve request context based on auth mode."""
    mode = settings.auth_mode.lower()
    if mode == "none":
        ctx = RequestContext(
            user_id="dev-user",
            user_role="ADMIN",
            tenant_id=settings.default_tenant_id,
            auth_mode=mode,
        )
        logger.debug("Resolved context (none): %s", ctx.model_dump())
        return ctx

    if mode == "dev_header":
        if not x_user_role or x_user_role not in settings.allowed_roles:
            raise HTTPException(status_code=401, detail="unauthorized: invalid or missing role")
        if not x_user_id:
            raise HTTPException(status_code=401, detail="unauthorized: missing user id")
        ctx = RequestContext(
            user_id=x_user_id,
            user_role=x_user_role,
            tenant_id=x_tenant_id or settings.default_tenant_id,
            auth_mode=mode,
        )
        logger.info(
            "Request context resolved user=%s role=%s tenant=%s mode=%s",
            ctx.user_id,
            ctx.user_role,
            ctx.tenant_id,
            ctx.auth_mode,
        )
        return ctx

    raise HTTPException(status_code=501, detail="auth mode not supported")


def context_dependency() -> Depends:
    return Depends(get_request_context)
