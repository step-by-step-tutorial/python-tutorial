import logging

from confluent_kafka.admin import AdminClient, NewTopic

logger = logging.getLogger(__name__)


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
