import logging

from sqlalchemy import text

from data_platform.audit.abstract_audit_service import AbstractAuditService
from data_platform.audit.audit_event import AuditEvent
from data_platform.audit.audit_event_converter import to_persistable_event
from data_platform.model.endpoints import AuditEndpoint
from data_platform.registry.connection_registry import connection_registry
from data_platform.util.file_utils import read_text_file

logger = logging.getLogger(__name__)


class AuditDatabaseService(AbstractAuditService):

    def __init__(self, audit_endpoint: AuditEndpoint) -> None:
        self._connection = connection_registry.get_item(audit_endpoint.database_connection_name)
        self._insert_event_sql = read_text_file(audit_endpoint.write_sql_files["write"])

    def save(self, event: AuditEvent) -> None:
        logger.debug("Persisting audit event to database: event_id=%s type=%s", event.event_id, event.event_type.value)
        with self._connection.begin() as connection:
            connection.execute(text(self._insert_event_sql), to_persistable_event(event))
        logger.info("Audit event persisted to database: event_id=%s type=%s", event.event_id, event.event_type.value)
