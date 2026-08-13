from app_config import env_config as ec
from sqlalchemy import text

from audit.audit_event_converter import to_audit_event_model
from factory.database_connection_factory import create_connection
from model.audit_event import AuditEvent
from util.file_utils import read_text_file

EVENT_INSERT_SQL = read_text_file("insert_audit_event.sql")


class AuditDatabaseService:

    def save(self, event: AuditEvent) -> None:
        with create_connection().begin() as connection:
            connection.execute(
                text(EVENT_INSERT_SQL),
                to_audit_event_model(event, ec.STREAMING_AUDIT_TOPIC)
            )
