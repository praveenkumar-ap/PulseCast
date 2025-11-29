from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping

from sqlalchemy.orm import Session

from ..core.logging import get_logger
from .base import BaseBatchAdapter, IngestionContext, IngestionResult
from .registry import registry

# Import adapters so they register on import
from .adapters import batch as batch_adapters  # noqa: F401
from .adapters import external as external_adapters  # noqa: F401

logger = get_logger(__name__)


def run_adapter(
    adapter_name: str,
    *,
    config: Mapping[str, Any],
    ctx: IngestionContext,
    db: Session,
) -> IngestionResult:
    """
    Execute a registered adapter with the supplied configuration and context.

    This entrypoint is intended for admin/ops workflows or CLI use.
    """
    adapter_cls: type[BaseBatchAdapter] = registry.get(adapter_name)
    adapter = adapter_cls()
    logger.info("Starting ingestion adapter=%s tenant=%s", adapter_name, ctx.tenant_id)
    result = adapter.ingest(db=db, ctx=ctx, config=config)
    logger.info(
        "Finished adapter=%s ingested=%s failed=%s",
        adapter_name,
        result.records_ingested,
        result.records_failed,
    )
    return result
