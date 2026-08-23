from sqlalchemy import text

from data_platform.audit.abstract_audit_service import AbstractAuditService
from data_platform.audit.audit_event_converter import to_persistable_event
from data_platform.model import AuditEndpoint
from data_platform.audit.audit_event import AuditEvent
from data_platform.registry.connection_registry import connection_registry
from data_platform.util.file_utils import read_text_file


class AuditDatabaseService(AbstractAuditService):

    def __init__(self, audit_endpoint: AuditEndpoint) -> None:
        self._connection = connection_registry.get_item(audit_endpoint.database_connection_name)
        self._insert_event_sql = read_text_file(audit_endpoint.write_sql_files["write"])

    def save(self, event: AuditEvent) -> None:
        with self._connection.begin() as connection:
            connection.execute(text(self._insert_event_sql), to_persistable_event(event))
