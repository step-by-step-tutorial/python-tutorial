import traceback
from dataclasses import asdict
from typing import Any

from model.audit_event import AuditEvent, AuditEventType, AuditStatus
from model.audit_task_context import AuditTaskContext


def create_started_event(context: AuditTaskContext) -> AuditEvent:
    return create_event(context, AuditEventType.TASK_STARTED, AuditStatus.STARTED)


def create_completed_event(context: AuditTaskContext, duration_ms: int) -> AuditEvent:
    return create_event(context, AuditEventType.TASK_COMPLETED, AuditStatus.SUCCEEDED, duration_ms=duration_ms)


def create_failed_event(context: AuditTaskContext, duration_ms: int, error: Exception) -> AuditEvent:
    return create_event(
        context,
        AuditEventType.TASK_FAILED,
        AuditStatus.FAILED,
        duration_ms=duration_ms,
        error_type=type(error).__name__,
        error_message=str(error),
        error_stacktrace=traceback.format_exc(),
    )


def create_event(context: AuditTaskContext, event_type: AuditEventType, status: AuditStatus, **event_fields: Any) -> AuditEvent:
    metrics_fields = asdict(context.metrics)
    event_data = metrics_fields | event_fields

    return AuditEvent(
        event_type=event_type,
        pipeline_name=context.pipeline_name,
        pipeline_id=context.pipeline_id,
        task_name=context.task_name,
        task_id=context.task_id,
        task_attempt=context.task_attempt,
        status=status,
        **event_data,
    )