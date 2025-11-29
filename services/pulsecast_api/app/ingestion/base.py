from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, ClassVar, Mapping, Optional
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session


class IngestionContext(BaseModel):
    """Execution context for an ingestion run."""

    tenant_id: str
    run_id: Optional[UUID | str] = Field(
        default=None, description="Optional run id used for lineage."
    )
    source_name: str = Field(description="Friendly name of the upstream source.")
    started_at: datetime = Field(default_factory=datetime.utcnow)
    extras: dict[str, Any] = Field(default_factory=dict)


class IngestionResult(BaseModel):
    """Summary result returned by every adapter."""

    records_ingested: int
    records_failed: int
    source_name: str
    started_at: datetime
    finished_at: datetime
    sample_ids: Optional[list[str]] = None
    notes: Optional[str] = None


class BaseBatchAdapter(ABC):
    """Abstract base class for batch ingestion adapters."""

    name: ClassVar[str]

    @abstractmethod
    def ingest(
        self,
        *,
        db: Session,
        ctx: IngestionContext,
        config: Mapping[str, Any],
    ) -> IngestionResult:
        """
        Execute ingestion for the provided configuration and context.

        Implementations must not mutate global state, and should not rely on
        hard-coded secrets or paths. Always read connection details from the
        supplied config or environment settings.
        """
        raise NotImplementedError
