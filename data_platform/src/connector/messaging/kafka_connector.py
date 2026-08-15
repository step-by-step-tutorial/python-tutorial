from config.messaging import settings as messaging_settings


def create_producer(bootstrap_servers: str | None = None) -> object:
    from confluent_kafka import Producer

    return Producer(
        {
            "bootstrap.servers": bootstrap_servers or messaging_settings.bootstrap_servers,
            "enable.idempotence": True,
            "acks": "all",
            "retries": 10,
            "delivery.timeout.ms": 120_000,
            "linger.ms": 10,
        }
    )
