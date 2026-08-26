import logging

from confluent_kafka import Producer

from test_data.config import settings as env_config

logger = logging.getLogger(__name__)


def create_producer():
    try:
        return Producer(
            {
                "bootstrap.servers": env_config.KAFKA_BOOTSTRAP_SERVERS,
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
