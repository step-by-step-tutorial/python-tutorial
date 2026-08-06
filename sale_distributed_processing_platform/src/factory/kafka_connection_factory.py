from confluent_kafka import Consumer, Producer

from app_config import env_config as ec

def create_kafka_producer() -> Producer:
    return Producer(
        {
            "bootstrap.servers": ec.KAFKA_BOOTSTRAP_SERVERS,
            "enable.idempotence": True,
            "acks": "all",
            "retries": 10,
            "delivery.timeout.ms": 120_000,
            "linger.ms": 10,
        }
    )

def create_topic_consumer() -> Consumer:
    return Consumer(
        {
            "bootstrap.servers": ec.KAFKA_BOOTSTRAP_SERVERS,
            "group.id": ec.KAFKA_SALE_TOPIC_CONSUMER_GROUP,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )


def create_audit_topic_consumer() -> Consumer:
    return Consumer(
        {
            "bootstrap.servers": ec.KAFKA_BOOTSTRAP_SERVERS,
            "group.id": ec.KAFKA_AUDIT_CONSUMER_GROUP,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
            "isolation.level": "read_committed",
        }
    )
