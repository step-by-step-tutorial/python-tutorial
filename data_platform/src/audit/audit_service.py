from audit.audit_archive_service import AuditArchiveService
from audit.audit_database_service import AuditDatabaseService
from audit.audit_log_service import AuditLogService
from audit.audit_messaging_service import AuditMessagingService
from dataset.definition import AuditEndpoint
from model.audit_event import AuditEvent


class AuditService:

    def __init__(self, audit_endpoint: AuditEndpoint) -> None:
        self._audit_endpoint = audit_endpoint
        self._log_service = AuditLogService()
        self._database_service = AuditDatabaseService(self._audit_endpoint)
        self._messaging_service = AuditMessagingService(self._audit_endpoint)
        self._archive_service = AuditArchiveService(self._audit_endpoint)

    def emit(self, event: AuditEvent) -> None:
        self._log_service.write(event)
        self._database_service.write(event)
        self._messaging_service.write(event)
        self._archive_service.write(event)
