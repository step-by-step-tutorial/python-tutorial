from sqlalchemy import text

from config.audit import settings as audit_settings
from audit.audit_event_converter import to_audit_event_model
from connector.database.postgres_connector import create_connection
from model.audit_event import AuditEvent
from util.file_utils import read_text_file


class AuditDatabaseService:

    def save(self, event: AuditEvent, streaming_topic: str | None = None) -> None:
        event_insert_sql = read_text_file("database/audit/insert_event.sql")
        with create_connection().begin() as connection:
            connection.execute(
                text(event_insert_sql),
                to_audit_event_model(event, streaming_topic or audit_settings.streaming_topic)
            )
