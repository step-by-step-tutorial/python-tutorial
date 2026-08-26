import logging

from data_platform.audit.abstract_audit_service import AbstractAuditService
from data_platform.audit.audit_event import AuditEvent

logger = logging.getLogger(__name__)


class AuditLogService(AbstractAuditService):

    def save(self, event: AuditEvent) -> None:
        logger.info(
            "Audit event: %s",
            {
                "event_id": str(event.event_id),
                "type": event.event_type.value,
                "status": event.status.value,
                "pipeline": event.pipeline_name,
                "task": event.task_name,
                "duration_ms": event.duration_ms,
                "source": event.source_uri,
                "destination": event.destination_uri,
                "input_rows": event.input_row_count,
                "output_rows": event.output_row_count,
                "error": event.error_message,
            },
        )

