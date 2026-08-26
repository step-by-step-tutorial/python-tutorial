import logging

from data_platform.audit.abstract_audit_service import AbstractAuditService
from data_platform.audit.audit_archive_service import AuditArchiveService
from data_platform.audit.audit_database_service import AuditDatabaseService
from data_platform.audit.audit_event import AuditEvent
from data_platform.audit.audit_log_service import AuditLogService
from data_platform.audit.audit_messaging_service import AuditMessagingService
from data_platform.model.endpoints import AuditEndpoint

logger = logging.getLogger(__name__)


class AuditService:

    def __init__(self, audit_endpoint: AuditEndpoint) -> None:
        self._write_services: list[AbstractAuditService] = [
            AuditLogService(),
            AuditDatabaseService(audit_endpoint),
            AuditMessagingService(audit_endpoint),
            AuditArchiveService(audit_endpoint),
        ]

    def emit(self, event: AuditEvent) -> None:
        logger.info("Emitting audit event: event_id=%s type=%s status=%s pipeline=%s task=%s", event.event_id,
                    event.event_type.value, event.status.value, event.pipeline_name, event.task_name)
        for write_service in self._write_services:
            logger.debug("Writing audit event: event_id=%s service=%s", event.event_id, type(write_service).__name__)
            write_service.save(event)
        logger.info("Audit event written to all sinks: event_id=%s type=%s", event.event_id, event.event_type.value)
