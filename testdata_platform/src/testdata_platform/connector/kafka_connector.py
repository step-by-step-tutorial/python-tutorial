import json
import logging
from collections.abc import Mapping, Sequence

from confluent_kafka import Producer

logger = logging.getLogger(__name__)


def create_producer(bootstrap_servers: str) -> Producer:
    try:
        return Producer(
            {
                "bootstrap.servers": bootstrap_servers,
                "enable.idempotence": True,
                "acks": "all",
                "retries": 1,
                "message.timeout.ms": 5_000,
                "delivery.timeout.ms": 5_000,
                "socket.timeout.ms": 2_000,
                "linger.ms": 10,
                "log_level": 0,
            }
        )
    except Exception:
        logger.error("Creating Kafka producer failed.")
        raise


def publish(
        bootstrap_servers: str,
        topic: str,
        rows: Sequence[Mapping[str, str]],
        key_column: str,
        flush_timeout_seconds: float,
) -> None:
    """Send each row as a JSON message keyed by key_column; raise if any message fails or is still pending."""
    producer = create_producer(bootstrap_servers)
    delivery_errors: list[str] = []

    def record_delivery(error, message) -> None:
        if error is not None:
            delivery_errors.append(str(error))

    for row in rows:
        producer.produce(
            topic=topic,
            key=str(row[key_column]),
            value=json.dumps(dict(row), ensure_ascii=False).encode("utf-8"),
            on_delivery=record_delivery,
        )
        producer.poll(0)

    pending_messages = producer.flush(flush_timeout_seconds)
    if delivery_errors:
        raise RuntimeError(f"Kafka delivery failed for {len(delivery_errors)} messages: {delivery_errors[0]}")
    if pending_messages:
        raise RuntimeError(f"Kafka delivery timed out with {pending_messages} messages still pending.")
