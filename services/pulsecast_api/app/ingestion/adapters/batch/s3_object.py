from __future__ import annotations

from io import BytesIO
from typing import Any, Mapping, Optional, Tuple

import boto3
import pandas as pd
from botocore.config import Config as BotoConfig
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
class S3ObjectAdapter(BaseBatchAdapter):
    """Load a single object from S3/MinIO into a target table."""

    name = "s3_object"

    def ingest(
        self,
        *,
        db: Session,
        ctx: IngestionContext,
        config: Mapping[str, Any],
    ) -> IngestionResult:
        bucket = config.get("bucket")
        key = config.get("key")
        file_format = config.get("file_format", "csv")
        target_table = config.get("target_table")
        endpoint_url = config.get("endpoint_url")  # optional for MinIO

        if not bucket or not key or not target_table:
            return IngestionResult(
                records_ingested=0,
                records_failed=0,
                source_name=self.name,
                started_at=ctx.started_at,
                finished_at=ctx.started_at,
                notes="bucket, key, and target_table are required",
            )

        s3 = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            config=BotoConfig(signature_version="s3v4"),
        )

        try:
            obj = s3.get_object(Bucket=bucket, Key=key)
            body = obj["Body"].read()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to fetch s3 object s3://%s/%s", bucket, key)
            return IngestionResult(
                records_ingested=0,
                records_failed=0,
                source_name=self.name,
                started_at=ctx.started_at,
                finished_at=ctx.started_at,
                notes=str(exc),
            )

        buffer = BytesIO(body)
        if file_format.lower() == "parquet":
            df = pd.read_parquet(buffer)
        else:
            df = pd.read_csv(buffer)

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
            return IngestionResult(
                records_ingested=len(df),
                records_failed=0,
                source_name=self.name,
                started_at=ctx.started_at,
                finished_at=pd.Timestamp.utcnow().to_pydatetime(),
            )
        except Exception as exc:  # noqa: BLE001
            db.rollback()
            logger.exception("S3 ingestion failed for s3://%s/%s", bucket, key)
            return IngestionResult(
                records_ingested=0,
                records_failed=len(df),
                source_name=self.name,
                started_at=ctx.started_at,
                finished_at=pd.Timestamp.utcnow().to_pydatetime(),
                notes=str(exc),
            )
