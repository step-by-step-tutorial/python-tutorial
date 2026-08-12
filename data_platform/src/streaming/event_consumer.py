import json

from app_config import env_config as ec
from factory.streamming_connection_factory import create_topic_consumer


class EventConsumer:
    def __init__(self) -> None:
        self.consumer = create_topic_consumer()
        self.consumer.subscribe([ec.STREAMING_TOPIC])

    def consume(self, timeout_seconds: float = 5.0) -> dict | None:
        message = self.consumer.poll(timeout_seconds)
        if message is None:
            return None

        if message.error():
            raise RuntimeError(str(message.error()))

        event = json.loads(message.value().decode("utf-8"))
        self.consumer.commit(message=message, asynchronous=False, )
        return event

    def close(self) -> None:
        self.consumer.close()
