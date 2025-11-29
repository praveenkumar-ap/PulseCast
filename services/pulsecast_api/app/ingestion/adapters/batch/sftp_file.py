from __future__ import annotations

import tempfile
from typing import Any, Mapping, Optional, Tuple

import pandas as pd
import paramiko
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
class SftpFileAdapter(BaseBatchAdapter):
    """Fetch a file over SFTP and load it into a target table."""

    name = "sftp_file"

    def ingest(
        self,
        *,
        db: Session,
        ctx: IngestionContext,
        config: Mapping[str, Any],
    ) -> IngestionResult:
        host = config.get("host")
        port = int(config.get("port", 22))
        username = config.get("username")
        password = config.get("password")
        key_path = config.get("key_path")
        remote_path = config.get("remote_path")
        file_format = config.get("file_format", "csv")
        target_table = config.get("target_table")

        if not host or not username or not remote_path or not target_table:
            return IngestionResult(
                records_ingested=0,
                records_failed=0,
                source_name=self.name,
                started_at=ctx.started_at,
                finished_at=ctx.started_at,
                notes="host, username, remote_path, and target_table are required",
            )

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            if key_path:
                ssh.connect(host, port=port, username=username, key_filename=key_path)
            else:
                ssh.connect(host, port=port, username=username, password=password)
            sftp = ssh.open_sftp()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to connect to SFTP host %s", host)
            return IngestionResult(
                records_ingested=0,
                records_failed=0,
                source_name=self.name,
                started_at=ctx.started_at,
                finished_at=ctx.started_at,
                notes=str(exc),
            )

        with tempfile.NamedTemporaryFile() as tmp:
            try:
                sftp.get(remote_path, tmp.name)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Failed to download %s", remote_path)
                return IngestionResult(
                    records_ingested=0,
                    records_failed=0,
                    source_name=self.name,
                    started_at=ctx.started_at,
                    finished_at=ctx.started_at,
                    notes=str(exc),
                )
            finally:
                sftp.close()
                ssh.close()

            if file_format.lower() == "parquet":
                df = pd.read_parquet(tmp.name)
            else:
                df = pd.read_csv(tmp.name)

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
            logger.exception("SFTP ingestion failed for %s", remote_path)
            return IngestionResult(
                records_ingested=0,
                records_failed=len(df),
                source_name=self.name,
                started_at=ctx.started_at,
                finished_at=pd.Timestamp.utcnow().to_pydatetime(),
                notes=str(exc),
            )
