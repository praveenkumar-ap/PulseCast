from __future__ import annotations

from typing import Dict, Iterable, Type

from .base import IndicatorSourceAdapter


class IndicatorAdapterRegistry:
    def __init__(self) -> None:
        self._adapters: Dict[str, Type[IndicatorSourceAdapter]] = {}

    def register(self, source_code: str, adapter_cls: Type[IndicatorSourceAdapter]) -> None:
        self._adapters[source_code] = adapter_cls

    def get(self, source_code: str) -> IndicatorSourceAdapter:
        cls = self._adapters.get(source_code)
        if not cls:
            raise KeyError(f"No adapter registered for {source_code}")
        return cls()

    def list_codes(self) -> Iterable[str]:
        return sorted(self._adapters.keys())


registry = IndicatorAdapterRegistry()


def register_adapter(source_code: str):
    def decorator(cls: Type[IndicatorSourceAdapter]) -> Type[IndicatorSourceAdapter]:
        registry.register(source_code, cls)
        return cls

    return decorator
