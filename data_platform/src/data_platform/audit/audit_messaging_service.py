import logging
from functools import partial

from data_platform.audit.abstract_audit_service import AbstractAuditService
from data_platform.audit.audit_event import AuditEvent
from data_platform.config.main_settings import settings as main_settings
from data_platform.model.endpoints import AuditEndpoint
from data_platform.registry.connection_registry import connection_registry
from data_platform.util.kafka_admin import ensure_topic_exists
from data_platform.util.kafka_utils import handle_kafka_response

logger = logging.getLogger(__name__)


class AuditMessagingService(AbstractAuditService):

    def __init__(self, audit_endpoint: AuditEndpoint) -> None:
        self._connection_name = audit_endpoint.messaging_connection_name
        self._channel_name = audit_endpoint.channel_name
        self._producer = connection_registry.get_item(self._connection_name)

    def save(self, event: AuditEvent) -> None:
        ensure_topic_exists(
            main_settings.messaging[self._connection_name].bootstrap_servers,
            self._channel_name,
        )
        logger.info(
            "Publishing audit event: event_id=%s type=%s status=%s topic=%s",
            event.event_id,
            event.event_type.value,
            event.status.value,
            self._channel_name,
        )

        try:
            self._producer.produce(
                topic=self._channel_name,
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
            logger.error(
                "Failed to publish audit event: event_id=%s topic=%s error=%s",
                event.event_id,
                self._channel_name,
                error,
            )
            raise
        logger.debug(
            "Audit event queued for Kafka: event_id=%s topic=%s",
            event.event_id,
            self._channel_name,
        )
