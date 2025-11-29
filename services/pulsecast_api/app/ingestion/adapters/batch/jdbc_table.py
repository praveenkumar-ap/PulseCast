from __future__ import annotations

from typing import Any, Mapping, Optional, Tuple

import pandas as pd
from sqlalchemy import create_engine, inspect
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
class JdbcTableAdapter(BaseBatchAdapter):
    """Copy a table from a JDBC/SQL source into Postgres."""

    name = "jdbc_table"

    def ingest(
        self,
        *,
        db: Session,
        ctx: IngestionContext,
        config: Mapping[str, Any],
    ) -> IngestionResult:
        source_url = config.get("url")
        source_table = config.get("table")
        source_schema = config.get("schema")
        incremental_column = config.get("incremental_column")
        last_value = config.get("last_value")
        target_table = config.get("target_table")

        if not source_url or not source_table or not target_table:
            return IngestionResult(
                records_ingested=0,
                records_failed=0,
                source_name=self.name,
                started_at=ctx.started_at,
                finished_at=ctx.started_at,
                notes="url, table, and target_table are required",
            )

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

        src_engine = create_engine(source_url)
        query = f"SELECT * FROM {source_table}"
        if source_schema:
            query = f"SELECT * FROM {source_schema}.{source_table}"
        if incremental_column and last_value is not None:
            query += f" WHERE {incremental_column} > '{last_value}'"

        try:
            df = pd.read_sql_query(query, src_engine)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to read source table %s", source_table)
            return IngestionResult(
                records_ingested=0,
                records_failed=0,
                source_name=self.name,
                started_at=ctx.started_at,
                finished_at=ctx.started_at,
                notes=str(exc),
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
            return IngestionResult(
                records_ingested=len(df),
                records_failed=0,
                source_name=self.name,
                started_at=ctx.started_at,
                finished_at=pd.Timestamp.utcnow().to_pydatetime(),
            )
        except Exception as exc:  # noqa: BLE001
            db.rollback()
            logger.exception("Failed to load into %s", target_table)
            return IngestionResult(
                records_ingested=0,
                records_failed=len(df),
                source_name=self.name,
                started_at=ctx.started_at,
                finished_at=pd.Timestamp.utcnow().to_pydatetime(),
                notes=str(exc),
            )
