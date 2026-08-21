from confluent_kafka import Producer

from test_data.config import settings as env_config


def create_producer() -> Producer:
    return Producer(
        {
            "bootstrap.servers": env_config.KAFKA_BOOTSTRAP_SERVERS,
            "enable.idempotence": True,
            "acks": "all",
            "retries": 10,
            "delivery.timeout.ms": 120_000,
            "linger.ms": 10,
        }
    )
