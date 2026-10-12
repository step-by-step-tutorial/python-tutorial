import logging

from confluent_kafka import Consumer, Producer
from confluent_kafka.admin import AdminClient, NewTopic

from data_platform.model.settings_model import MessagingSettingsModel

logger = logging.getLogger(__name__)


def create_producer(settings: MessagingSettingsModel) -> Producer:
    return Producer(
        {
            "bootstrap.servers": settings.bootstrap_servers,
            "enable.idempotence": True,
            "acks": "all",
            "retries": 10,
            "delivery.timeout.ms": 120_000,
            "linger.ms": 10,
        }
    )


def create_consumer(settings: MessagingSettingsModel) -> Consumer:
    return Consumer(
        {
            "bootstrap.servers": settings.bootstrap_servers,
            "group.id": "data-platform-messaging",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )


def ensure_topic_exists(
        bootstrap_servers: str,
        topic_name: str,
        partitions: int = 3,
        replication_factor: int = 1,
) -> None:
    if not bootstrap_servers or not topic_name:
        return

    try:
        admin_client = AdminClient({"bootstrap.servers": bootstrap_servers})
        topic = NewTopic(topic_name, num_partitions=partitions, replication_factor=replication_factor)
        futures = admin_client.create_topics([topic], request_timeout=5)
        future = futures.get(topic_name)
        if future is not None:
            future.result(timeout=5)
        logger.info("Ensured Kafka topic exists: %s", topic_name)
    except Exception as error:
        logger.warning("Unable to ensure Kafka topic %s exists: %s", topic_name, error)


def handle_delivery_report(error, message, event_id: str) -> None:
    if error is not None:
        logger.error("Failed to deliver event %s to topic=%s: %s", event_id, message.topic(), error)
    else:
        logger.info("Delivered event %s to topic=%s", event_id, message.topic())
