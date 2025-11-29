from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping

from sqlalchemy.orm import Session

from ...core.logging import get_logger
from ...ingestion.base import BaseBatchAdapter, IngestionContext, IngestionResult
from ...ingestion.registry import register_adapter

logger = get_logger(__name__)


class _EnterpriseStub(BaseBatchAdapter):
    """Base class for enterprise stubs with shared logic."""

    stub_description: str = "Enterprise connector stub"

    def ingest(
        self,
        *,
        db: Session,  # noqa: ARG002
        ctx: IngestionContext,
        config: Mapping[str, Any],
    ) -> IngestionResult:
        logger.info("%s not implemented. Config=%s", self.name, {**config})
        return IngestionResult(
            records_ingested=0,
            records_failed=0,
            source_name=self.name,
            started_at=ctx.started_at,
            finished_at=datetime.utcnow(),
            notes=f"Not implemented: {self.stub_description}",
        )


@register_adapter
class SAPODataAdapter(_EnterpriseStub):
    """Stub for SAP OData ingestion. Validates config and returns a stub result."""

    name = "sap_odata"
    stub_description = "SAP OData ingestion"


@register_adapter
class SalesforceAdapter(_EnterpriseStub):
    """Stub for Salesforce ingestion."""

    name = "salesforce"
    stub_description = "Salesforce ingestion"


@register_adapter
class EhrFhirAdapter(_EnterpriseStub):
    """Stub for EHR FHIR ingestion."""

    name = "ehr_fhir"
    stub_description = "EHR FHIR ingestion"
