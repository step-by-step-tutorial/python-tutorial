import json
from collections.abc import Callable
from typing import Any

from app_config import env_config as ec
from sqlalchemy import text

from converter.audit_event_converter import to_audit_pipeline_model, to_audit_task_model
from factory.database_connection_factory import create_connection
from model.audit_event import AuditEvent, AuditEventType
from util.file_utils import read_sql_file

EVENT_INSERT_SQL = read_sql_file("insert_audit_event.sql")
PIPELINE_STARTED_SQL = read_sql_file("insert_audit_pipeline_started.sql")
PIPELINE_FINISHED_SQL = read_sql_file("update_audit_pipeline_finished.sql")
TASK_STARTED_SQL = read_sql_file("insert_audit_task_started.sql")
TASK_FINISHED_SQL = read_sql_file("update_audit_task_finished.sql")

AUDIT_MODEL_OPERATIONS: dict[AuditEventType, tuple[str, Callable[[AuditEvent], dict[str, Any]]]] = {
    AuditEventType.PIPELINE_STARTED: (PIPELINE_STARTED_SQL, to_audit_pipeline_model),
    AuditEventType.PIPELINE_COMPLETED: (PIPELINE_FINISHED_SQL, to_audit_pipeline_model),
    AuditEventType.PIPELINE_FAILED: (PIPELINE_FINISHED_SQL, to_audit_pipeline_model),
    AuditEventType.TASK_STARTED: (TASK_STARTED_SQL, to_audit_task_model),
    AuditEventType.TASK_COMPLETED: (TASK_FINISHED_SQL, to_audit_task_model),
    AuditEventType.TASK_FAILED: (TASK_FINISHED_SQL, to_audit_task_model)
}


class AuditDatabaseService:

    def save(self, event: AuditEvent) -> None:
        parameters = event.model_dump(mode="json")
        parameters["metadata"] = json.dumps(parameters["metadata"])
        parameters["streaming_topic"] = ec.STREAMING_AUDIT_TOPIC

        with create_connection().begin() as connection:
            connection.execute(text(EVENT_INSERT_SQL), parameters)

            operation = AUDIT_MODEL_OPERATIONS.get(event.event_type)

            if operation is not None:
                sql, converter = operation
                connection.execute(text(sql), converter(event))
