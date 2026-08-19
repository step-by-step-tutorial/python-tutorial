from audit.audit_archive_service import AuditArchiveService
from audit.audit_database_service import AuditDatabaseService
from audit.audit_log_service import AuditLogService
from audit.audit_messaging_service import AuditMessagingService
from audit.abstract_audit_service import AbstractAuditService
from dataset.definition import AuditEndpoint
from model.audit_event import AuditEvent


class AuditService:

    def __init__(self, audit_endpoint: AuditEndpoint) -> None:
        self._write_services: list[AbstractAuditService] = [
            AuditLogService(),
            AuditDatabaseService(audit_endpoint),
            AuditMessagingService(audit_endpoint),
            AuditArchiveService(audit_endpoint),
        ]

    def emit(self, event: AuditEvent) -> None:
        for write_service in self._write_services:
            write_service.write(event)
