"""
Pluggable ingestion adapter framework for PulseCast.

Adapters live under app.ingestion.adapters and are registered via the registry.
Use run_adapter.run_adapter(...) to invoke a specific adapter with a config and
ingestion context.
"""

from .registry import registry, register_adapter

__all__ = ["registry", "register_adapter"]
