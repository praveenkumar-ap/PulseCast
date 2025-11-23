from __future__ import annotations

from ..core.config import settings
from .base import StreamingConsumerBase
from .kafka_consumer import KafkaStreamingConsumer


class StreamingDisabled(Exception):
    """Raised when streaming provider is disabled."""


def get_streaming_consumer() -> StreamingConsumerBase:
    provider = (settings.stream_provider or "none").lower()
    if provider == "kafka":
        return KafkaStreamingConsumer()
    if provider == "none":
        raise StreamingDisabled("Streaming provider disabled")
    raise StreamingDisabled(f"Unsupported streaming provider: {provider}")
