from typing import Any

from model.audit_event import AuditEvent


def to_audit_pipeline_model(event: AuditEvent) -> dict[str, Any]:
    return {
        "pipeline_id": event.pipeline_id,
        "pipeline_name": event.pipeline_name,
        "airflow_dag_id": event.metadata.get("airflow_dag_id"),
        "airflow_dag_run_id": event.metadata.get("airflow_dag_run_id"),
        "logical_date": event.metadata.get("logical_date"),
        "started_at": event.event_time,
        "completed_at": event.event_time,
        "status": event.status.value,
        "input_row_count": event.input_row_count,
        "output_row_count": event.output_row_count,
        "rejected_row_count": event.rejected_row_count,
        "duration_ms": event.duration_ms,
        "error_message": event.error_message
    }


def to_audit_task_model(event: AuditEvent) -> dict[str, Any]:
    return {
        "task_id": event.task_id,
        "pipeline_id": event.pipeline_id,
        "task_name": event.task_name,
        "task_attempt": event.task_attempt,
        "started_at": event.event_time,
        "completed_at": event.event_time,
        "status": event.status.value,
        "input_row_count": event.input_row_count,
        "output_row_count": event.output_row_count,
        "rejected_row_count": event.rejected_row_count,
        "duration_ms": event.duration_ms,
        "error_type": event.error_type,
        "error_message": event.error_message
    }
