from __future__ import annotations

import abc
from typing import Any, Dict, List


class StreamingConsumerBase(abc.ABC):
    """Abstract base class for streaming consumers."""

    @abc.abstractmethod
    def subscribe(self) -> None:
        """Subscribe to stream/topic."""

    @abc.abstractmethod
    def poll(self, batch_size: int) -> List[Dict[str, Any]]:
        """Poll and return a batch of messages as dicts."""

    @abc.abstractmethod
    def ack(self) -> None:
        """Commit/acknowledge offsets/messages."""

    def close(self) -> None:
        """Optional cleanup."""
        return None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
