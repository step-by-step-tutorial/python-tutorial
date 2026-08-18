import logging

from audit.base import AuditWriteService
from model.audit_event import AuditEvent

logger = logging.getLogger(__name__)


class AuditLogService(AuditWriteService):

    def write(self, event: AuditEvent) -> None:
        logger.info("Audit event: %s", event.model_dump_json())
