import json

from confluent_kafka import Consumer

from app_config import env_config as ec


class SaleEventConsumer:
    def __init__(self) -> None:
        self.consumer = Consumer(
            {
                "bootstrap.servers": ec.KAFKA_BOOTSTRAP_SERVERS,
                "group.id": "sale-platform-consumer",
                "auto.offset.reset": "earliest",
                "enable.auto.commit": False,
            }
        )
        self.consumer.subscribe([ec.KAFKA_TOPIC])

    def consume_sale_event(self, timeout_seconds: float = 5.0) -> dict | None:
        message = self.consumer.poll(timeout_seconds)
        if message is None:
            return None

        if message.error():
            raise RuntimeError(str(message.error()))

        sale_event = json.loads(message.value().decode("utf-8"))
        self.consumer.commit(message=message, asynchronous=False, )
        return sale_event

    def close(self) -> None:
        self.consumer.close()
