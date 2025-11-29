from __future__ import annotations

from typing import Dict, List, Type

from .base import BaseBatchAdapter


class AdapterRegistry:
    """Registry for ingestion adapters."""

    def __init__(self) -> None:
        self._adapters: Dict[str, Type[BaseBatchAdapter]] = {}

    def register(self, adapter_cls: Type[BaseBatchAdapter]) -> None:
        if not adapter_cls.name:
            raise ValueError(f"Adapter {adapter_cls} is missing a name")
        key = adapter_cls.name
        if key in self._adapters:
            # Overwrite is intentional to allow upgrades; log would happen at import-time
            self._adapters[key] = adapter_cls
            return
        self._adapters[key] = adapter_cls

    def get(self, name: str) -> Type[BaseBatchAdapter]:
        try:
            return self._adapters[name]
        except KeyError as exc:  # noqa: B904
            raise KeyError(f"Adapter '{name}' is not registered") from exc

    def list(self) -> List[str]:
        return sorted(self._adapters.keys())


registry = AdapterRegistry()


def register_adapter(cls: Type[BaseBatchAdapter]) -> Type[BaseBatchAdapter]:
    registry.register(cls)
    return cls


__all__ = ["registry", "register_adapter", "AdapterRegistry"]
