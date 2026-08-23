import logging

from data_platform.audit.abstract_audit_service import AbstractAuditService
from data_platform.model.audit_event import AuditEvent

logger = logging.getLogger(__name__)


class AuditLogService(AbstractAuditService):

    def write(self, event: AuditEvent) -> None:
        logger.info(
            "Audit event: %s",
            f"Pipeline={event.pipeline_name}, Task={event.task_name}, ID={event.event_id}",
        )
