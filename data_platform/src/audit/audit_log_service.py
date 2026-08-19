import logging

from audit.abstract_audit_service import AbstractAuditService
from model.audit_event import AuditEvent

logger = logging.getLogger(__name__)


class AuditLogService(AbstractAuditService):

    def write(self, event: AuditEvent) -> None:
        logger.info(f"Audit event: "
                    f"Pipeline={event.pipeline_name}, "
                    f"Task={event.task_name}, "
                    f"ID={event.event_id}")
