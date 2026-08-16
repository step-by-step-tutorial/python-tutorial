import logging
from functools import partial
from collections.abc import Callable
from typing import Any

from model.audit_event import AuditEvent
from streaming.delivery import topic_on_delivery

logger = logging.getLogger(__name__)


class AuditStreamingService:

    def __init__(self, topic: str, producer: Any | None = None, producer_factory: Callable[[], Any] | None = None) -> None:
        self.topic = topic
        self._producer = producer
        self._producer_factory = producer_factory

    def _get_producer(self) -> Any:
        if self._producer is None:
            if self._producer_factory is None:
                from connector.messaging.kafka_connector import create_producer

                self._producer_factory = create_producer
            self._producer = self._producer_factory()
        return self._producer

    def publish(self, event: AuditEvent) -> None:
        logger.info("Publishing audit event %s to streaming topic %s", event.event_id, self.topic)

        try:
            self._get_producer().produce(
                topic=self.topic,
                key=str(event.event_id),
                value=event.model_dump_json(),
                headers={
                    "event_type": event.event_type.value,
                    "event_version": str(event.event_version)
                },
                on_delivery=partial(topic_on_delivery, event_id=str(event.event_id))
            )
            self._get_producer().poll(0)
        except Exception as error:
            logger.exception("Failed to publish audit event %s due to error: %s", event.event_id, error)
            raise
