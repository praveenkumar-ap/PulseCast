import os
from typing import Optional

import psycopg


def get_connection() -> psycopg.Connection:
    """Create a psycopg connection using env vars with sensible defaults."""
    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT", "5432"))
    dbname = os.getenv("DB_NAME", "pulsecast")
    user = os.getenv("DB_USER", "pulsecast")
    password = os.getenv("DB_PASSWORD", "pulsecast")

    return psycopg.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
    )
