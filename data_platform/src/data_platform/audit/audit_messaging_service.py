import logging
from functools import partial

from data_platform.audit.abstract_audit_service import AbstractAuditService
from data_platform.config.main_settings import settings as main_settings
from data_platform.model import AuditEndpoint
from data_platform.model.audit_event import AuditEvent
from data_platform.registry.connection_registry import connection_registry
from data_platform.util.kafka_admin import ensure_topic_exists
from data_platform.util.kafka_utils import handle_kafka_response

logger = logging.getLogger(__name__)


class AuditMessagingService(AbstractAuditService):

    def __init__(self, audit_endpoint: AuditEndpoint) -> None:
        self.connection_name = audit_endpoint.messaging_connection_name
        self.channel_name = audit_endpoint.channel_name
        self._producer = connection_registry.get_item(self.connection_name)

    def write(self, event: AuditEvent) -> None:
        ensure_topic_exists(
            main_settings.messaging[self.connection_name].bootstrap_servers,
            self.channel_name,
        )
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
                on_delivery=partial(handle_kafka_response, event_id=str(event.event_id))
            )
            self._producer.poll(0)
        except Exception as error:
            logger.exception("Failed to publish audit event %s due to error: %s", event.event_id, error)
            raise
