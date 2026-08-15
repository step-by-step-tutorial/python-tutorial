import logging

from model.audit_event import AuditEvent

logger = logging.getLogger("audit")


class AuditLogService:

    def log(self, event: AuditEvent) -> None:
        logger.info("Audit event: %s", event.event_id)
