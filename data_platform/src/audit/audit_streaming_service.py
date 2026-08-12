import logging
from functools import partial

from factory.streamming_connection_factory import create_streaming_producer
from model.audit_event import AuditEvent
from util.streaming_utils import topic_on_delivery

logger = logging.getLogger(__name__)


class AuditStreamingService:

    def __init__(self, topic: str) -> None:
        self.topic = topic
        self.producer = create_streaming_producer()

    def publish(self, event: AuditEvent) -> None:
        logger.info("Publishing audit event %s to streaming topic %s", event.event_id, self.topic)

        try:
            self.producer.produce(
                topic=self.topic,
                key=str(event.event_id),
                value=event.model_dump_json(),
                headers={
                    "event_type": event.event_type.value,
                    "event_version": str(event.event_version)
                },
                on_delivery=partial(topic_on_delivery, event_id=str(event.event_id))
            )
            self.producer.poll(0)
        except Exception as error:
            logger.exception("Failed to publish audit event %s due to error: %s", event.event_id, error)
            raise
