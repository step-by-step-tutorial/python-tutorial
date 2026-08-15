from confluent_kafka import Producer

from app_config import env_config as ec


def create_producer() -> Producer:
    return Producer(
        {
            "bootstrap.servers": ec.APP_STREAMING_BOOTSTRAP_SERVERS,
            "enable.idempotence": True,
            "acks": "all",
            "retries": 10,
            "delivery.timeout.ms": 120_000,
            "linger.ms": 10,
        }
    )
