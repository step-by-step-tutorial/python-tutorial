import logging

from audit.abstract_audit_service import AbstractAuditService
from model.audit_event import AuditEvent

logger = logging.getLogger(__name__)


class AuditLogService(AbstractAuditService):

    def write(self, event: AuditEvent) -> None:
        logger.info("Audit event: %s", event.model_dump_json())
