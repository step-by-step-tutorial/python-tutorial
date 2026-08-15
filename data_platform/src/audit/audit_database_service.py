from app_config import env_config as ec
from sqlalchemy import text

from audit.audit_event_converter import to_audit_event_model
from connector.database.postgres_connector import create_connection
from model.audit_event import AuditEvent
from util.file_utils import read_text_file

EVENT_INSERT_SQL = read_text_file("database/audit/insert_event.sql")


class AuditDatabaseService:

    def save(self, event: AuditEvent, streaming_topic: str | None = None) -> None:
        with create_connection().begin() as connection:
            connection.execute(
                text(EVENT_INSERT_SQL),
                to_audit_event_model(event, streaming_topic or ec.APP_STREAMING_AUDIT_TOPIC)
            )
