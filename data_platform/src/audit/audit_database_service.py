from __future__ import annotations

from sqlalchemy import text

from audit.audit_event_converter import to_persistable_event
from audit.abstract_audit_service import AbstractAuditService
from connector.registry import get_connection
from dataset.definition import AuditEndpoint
from model.audit_event import AuditEvent
from util.file_utils import read_text_file


class AuditDatabaseService(AbstractAuditService):

    def __init__(self, audit_endpoint: AuditEndpoint) -> None:
        self._connection = get_connection(audit_endpoint.database_connection_name)
        self._insert_event_sql = read_text_file(audit_endpoint.write_sql_files["write"])

    def write(self, event: AuditEvent) -> None:
        with self._connection.begin() as connection:
            connection.execute(text(self._insert_event_sql), to_persistable_event(event))
