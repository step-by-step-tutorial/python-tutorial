import json
from collections.abc import Callable
from typing import Any

from sqlalchemy import text

from converter.audit_event_converter import to_audit_pipeline_model, to_audit_task_model
from factory.database_connection_factory import create_connection
from model.audit_event import AuditEvent
from model.data_quality_result import DataQualityResult
from util.file_utils import read_sql_file

EVENT_INSERT_SQL = read_sql_file("insert_audit_event.sql")
QUALITY_RESULT_INSERT_SQL = read_sql_file("insert_audit_data_quality_result.sql")
PIPELINE_RUN_EXISTS_SQL = read_sql_file("select_audit_pipeline_exists.sql")
PIPELINE_STARTED_SQL = read_sql_file("insert_audit_pipeline_started.sql")
PIPELINE_FINISHED_SQL = read_sql_file("update_audit_pipeline_finished.sql")
TASK_STARTED_SQL = read_sql_file("insert_audit_task_started.sql")
TASK_FINISHED_SQL = read_sql_file("update_audit_task_finished.sql")

AUDIT_MODEL_OPERATIONS: dict[str, tuple[str, Callable[[AuditEvent], dict[str, Any]]]] = {
    "PIPELINE_STARTED": (PIPELINE_STARTED_SQL, to_audit_pipeline_model),
    "PIPELINE_COMPLETED": (PIPELINE_FINISHED_SQL, to_audit_pipeline_model),
    "PIPELINE_FAILED": (PIPELINE_FINISHED_SQL, to_audit_pipeline_model),
    "TASK_STARTED": (TASK_STARTED_SQL, to_audit_task_model),
    "TASK_COMPLETED": (TASK_FINISHED_SQL, to_audit_task_model),
    "TASK_FAILED": (TASK_FINISHED_SQL, to_audit_task_model),
}


def save_event(event: AuditEvent, kafka_topic: str) -> None:
    model = event.model_dump(mode="json")
    model.update(
        metadata=json.dumps(model["metadata"]),
        kafka_topic=kafka_topic
    )

    with create_connection().begin() as connection:
        connection.execute(text(EVENT_INSERT_SQL), model)
        if (operation := AUDIT_MODEL_OPERATIONS.get(event.event_type)) is not None:
            sql, converter = operation
            connection.execute(text(sql), converter(event))


def save_data_quality_result(result: DataQualityResult) -> None:
    parameters = result.model_dump(mode="json")
    parameters["metadata"] = json.dumps(parameters["metadata"])

    with create_connection().begin() as connection:
        connection.execute(text(QUALITY_RESULT_INSERT_SQL), parameters)


def is_pipeline_exists(pipeline_id: str) -> bool:
    with create_connection().connect() as connection:
        return bool(
            connection.execute(
                text(PIPELINE_RUN_EXISTS_SQL),
                {"pipeline_id": pipeline_id},
            ).scalar_one()
        )
