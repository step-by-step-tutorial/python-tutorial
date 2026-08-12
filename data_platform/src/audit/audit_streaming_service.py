import logging

from app_config import env_config as ec
from factory.streamming_connection_factory import create_streaming_producer
from model.audit_event import AuditEvent
from util.streaming_utils import delivery_callback, flush_messages

logger = logging.getLogger(__name__)


class AuditStreamingService:

    def __init__(self) -> None:
        self.producer = create_streaming_producer()

    def publish(self, event: AuditEvent) -> None:
        logger.info("Publishing audit event to streaming topic %r", ec.STREAMING_AUDIT_TOPIC)

        try:
            self.producer.produce(
                topic=ec.STREAMING_AUDIT_TOPIC,
                key=event.pipeline_id,
                value=event.model_dump_json(),
                headers={
                    "event_id": str(event.event_id),
                    "event_type": event.event_type.value,
                    "event_version": str(event.event_version)
                },
                on_delivery=delivery_callback
            )
            self.producer.poll(0)
        except Exception as error:
            logger.exception("Failed to publish audit event due to error: %s", error)
            raise

    def flush(self) -> None:
        flush_messages(self.producer)