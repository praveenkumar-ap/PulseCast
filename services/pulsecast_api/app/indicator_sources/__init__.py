"""
Generic indicator source adapters, registry, and ingestion orchestration.
"""

from .registry import registry, register_adapter
from .ingest import ingest_active_sources

__all__ = ["registry", "register_adapter", "ingest_active_sources"]
