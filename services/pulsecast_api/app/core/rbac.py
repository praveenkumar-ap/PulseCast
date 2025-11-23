from __future__ import annotations

from typing import Callable

from fastapi import Depends, HTTPException

from .context import RequestContext, get_request_context


def require_roles(*allowed_roles: str) -> Callable[[RequestContext], RequestContext]:
    """Return a dependency that enforces the caller's role."""

    async def _checker(ctx: RequestContext = Depends(get_request_context)) -> RequestContext:
        if ctx.user_role is None or ctx.user_role not in allowed_roles:
            raise HTTPException(status_code=403, detail="forbidden: role not allowed")
        return ctx

    return _checker

