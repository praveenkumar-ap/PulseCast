from __future__ import annotations

import json
import logging
from typing import Any, Dict

from kafka import KafkaProducer  # type: ignore

from services.pulsecast_api.app.core.config import settings

logger = logging.getLogger(__name__)


class SignalsProducer:
    def __init__(self) -> None:
        if not settings.kafka_bootstrap_servers or not settings.stream_signals_topic:
            raise RuntimeError("Kafka producer settings missing")
        self.topic = settings.stream_signals_topic
        self.producer = KafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers.split(","),
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

    def send(self, event: Dict[str, Any]) -> None:
        self.producer.send(self.topic, value=event)

    def flush(self) -> None:
        self.producer.flush()

    def close(self) -> None:
        try:
            self.producer.flush()
            self.producer.close()
        except Exception:  # noqa: BLE001
            logger.warning("Error closing Kafka producer", exc_info=True)
