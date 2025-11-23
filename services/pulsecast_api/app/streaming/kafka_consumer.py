from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from ..core.config import settings
from .base import StreamingConsumerBase

logger = logging.getLogger(__name__)


class KafkaStreamingConsumer(StreamingConsumerBase):
    """Kafka/Redpanda consumer implementation."""

    def __init__(self) -> None:
        try:
            from kafka import KafkaConsumer  # type: ignore
            from kafka.errors import NoBrokersAvailable  # type: ignore
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("kafka-python is required for KafkaStreamingConsumer") from exc

        if not settings.kafka_bootstrap_servers or not settings.stream_signals_topic:
            raise RuntimeError("Kafka settings missing")

        self.topic = settings.stream_signals_topic
        self.batch_size = settings.stream_max_batch_size
        try:
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=settings.kafka_bootstrap_servers.split(","),
                group_id=settings.stream_group_id_signals_consumer or "pulsecast-signals-consumer",
                enable_auto_commit=False,
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            )
        except NoBrokersAvailable as exc:
            logger.error("No Kafka brokers available at %s", settings.kafka_bootstrap_servers)
            raise RuntimeError("Kafka brokers not available; start Redpanda/Kafka and retry") from exc

    def subscribe(self) -> None:
        # subscription handled in constructor for kafka-python consumer
        logger.info("Subscribed to topic=%s", self.topic)

    def poll(self, batch_size: int) -> List[Dict[str, Any]]:
        msgs = self.consumer.poll(timeout_ms=settings.stream_poll_interval_ms, max_records=batch_size)
        records: List[Dict[str, Any]] = []
        for _, batch in msgs.items():
            for msg in batch:
                if isinstance(msg.value, dict):
                    records.append(msg.value)
        logger.info("Polled %s messages from topic=%s", len(records), self.topic)
        return records

    def ack(self) -> None:
        self.consumer.commit()

    def close(self) -> None:
        try:
            self.consumer.close()
        except Exception:  # noqa: BLE001
            logger.warning("Error closing Kafka consumer", exc_info=True)
