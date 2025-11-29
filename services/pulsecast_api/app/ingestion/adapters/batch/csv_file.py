from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Optional, Tuple

import pandas as pd
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from ...core.logging import get_logger
from ...ingestion.base import BaseBatchAdapter, IngestionContext, IngestionResult
from ...ingestion.registry import register_adapter

logger = get_logger(__name__)


def _split_target(target_table: str) -> Tuple[Optional[str], str]:
    if "." in target_table:
        schema, table = target_table.split(".", 1)
        return schema, table
    return None, target_table


@register_adapter
class CsvFileAdapter(BaseBatchAdapter):
    """Load a local/mounted CSV file into a target table."""

    name = "csv_file"

    def ingest(
        self,
        *,
        db: Session,
        ctx: IngestionContext,
        config: Mapping[str, Any],
    ) -> IngestionResult:
        path = config.get("path")
        delimiter = config.get("delimiter", ",")
        target_table = config.get("target_table")
        if not path or not target_table:
            return IngestionResult(
                records_ingested=0,
                records_failed=0,
                source_name=self.name,
                started_at=ctx.started_at,
                finished_at=ctx.started_at,
                notes="path and target_table are required",
            )

        csv_path = Path(path)
        if not csv_path.exists():
            return IngestionResult(
                records_ingested=0,
                records_failed=0,
                source_name=self.name,
                started_at=ctx.started_at,
                finished_at=ctx.started_at,
                notes=f"file not found: {path}",
            )

        df = pd.read_csv(csv_path, delimiter=delimiter)
        schema, table = _split_target(target_table)

        inspector = inspect(db.get_bind())
        if table not in inspector.get_table_names(schema=schema):
            return IngestionResult(
                records_ingested=0,
                records_failed=0,
                source_name=self.name,
                started_at=ctx.started_at,
                finished_at=ctx.started_at,
                notes=f"target table {target_table} does not exist",
            )

        try:
            df.to_sql(
                name=table,
                con=db.get_bind(),
                schema=schema,
                if_exists="append",
                index=False,
                method="multi",
            )
            db.commit()
            ingested = len(df)
            return IngestionResult(
                records_ingested=ingested,
                records_failed=0,
                source_name=self.name,
                started_at=ctx.started_at,
                finished_at=pd.Timestamp.utcnow().to_pydatetime(),
            )
        except Exception as exc:  # noqa: BLE001
            db.rollback()
            logger.exception("CSV ingestion failed for %s", path)
            return IngestionResult(
                records_ingested=0,
                records_failed=len(df),
                source_name=self.name,
                started_at=ctx.started_at,
                finished_at=pd.Timestamp.utcnow().to_pydatetime(),
                notes=str(exc),
            )
