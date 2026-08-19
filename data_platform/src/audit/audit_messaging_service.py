import logging
from functools import partial

from audit.abstract_audit_service import AbstractAuditService
from connector.kafka_connection_factory import get_connection
from dataset.definition import AuditEndpoint
from model.audit_event import AuditEvent
from streaming.delivery import topic_on_delivery

logger = logging.getLogger(__name__)


class AuditMessagingService(AbstractAuditService):

    def __init__(self, audit_endpoint: AuditEndpoint) -> None:
        self.connection_name = audit_endpoint.messaging_connection_name
        self.channel_name = audit_endpoint.channel_name
        self._producer = get_connection(self.connection_name)

    def write(self, event: AuditEvent) -> None:
        logger.info("Publishing audit event %s to messaging channel %s", event.event_id, self.channel_name)

        try:
            self._producer.produce(
                topic=self.channel_name,
                key=str(event.event_id),
                value=event.model_dump_json(),
                headers={
                    "event_type": event.event_type.value,
                    "event_version": str(event.event_version)
                },
                on_delivery=partial(topic_on_delivery, event_id=str(event.event_id))
            )
            self._producer.poll(0)
        except Exception as error:
            logger.exception("Failed to publish audit event %s due to error: %s", event.event_id, error)
            raise
