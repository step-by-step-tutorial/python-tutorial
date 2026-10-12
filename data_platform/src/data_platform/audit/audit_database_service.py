import logging

from sqlalchemy import text

from data_platform.audit.abstract_audit_service import AbstractAuditService
from data_platform.model.audit_event_model import AuditEventModel
from data_platform.model.endpoint_model import AuditEndpointModel
from data_platform.registry.connection_registry import connection_registry
from data_platform.util.file_utils import read_text_file

logger = logging.getLogger(__name__)


class AuditDatabaseService(AbstractAuditService):

    def __init__(self, audit_endpoint: AuditEndpointModel) -> None:
        self._connection = connection_registry.get_item(audit_endpoint.database_connection_name)
        self._insert_event_sql = read_text_file(audit_endpoint.write_sql_files["write"])

    def save(self, event: AuditEventModel) -> None:
        logger.debug("Persisting audit event to database: event_id=%s type=%s", event.event_id, event.event_type.value)
        with self._connection.begin() as connection:
            connection.execute(text(self._insert_event_sql), event.to_persistable())
        logger.info("Audit event persisted to database: event_id=%s type=%s", event.event_id, event.event_type.value)
