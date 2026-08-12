import traceback
from dataclasses import asdict

from model.audit_event import AuditEvent, AuditEventType, AuditStatus
from model.audit_task_context import AuditTaskContext


class AuditEventFactory:

    @staticmethod
    def create_pipeline_started_event(pipeline_name: str, pipeline_id: str, metadata: dict | None = None) -> AuditEvent:
        return AuditEvent(
            event_type=AuditEventType.PIPELINE_STARTED,
            pipeline_name=pipeline_name,
            pipeline_id=pipeline_id,
            status=AuditStatus.STARTED,
            metadata=metadata or {}
        )

    @staticmethod
    def create_pipeline_completed_event(
            pipeline_name: str,
            pipeline_id: str,
            duration_ms: int,
            input_row_count: int | None = None,
            output_row_count: int | None = None,
            rejected_row_count: int | None = None,
            metadata: dict | None = None
    ) -> AuditEvent:
        return AuditEvent(
            event_type=AuditEventType.PIPELINE_COMPLETED,
            pipeline_name=pipeline_name,
            pipeline_id=pipeline_id,
            status=AuditStatus.SUCCEEDED,
            input_row_count=input_row_count,
            output_row_count=output_row_count,
            rejected_row_count=rejected_row_count,
            duration_ms=duration_ms,
            metadata=metadata or {}
        )

    @staticmethod
    def create_pipeline_failed_event(pipeline_name: str, pipeline_id: str, duration_ms: int, error: Exception, metadata: dict | None = None) -> AuditEvent:
        return AuditEvent(
            event_type=AuditEventType.PIPELINE_FAILED,
            pipeline_name=pipeline_name,
            pipeline_id=pipeline_id,
            status=AuditStatus.FAILED,
            duration_ms=duration_ms,
            error_type=type(error).__name__,
            error_message=str(error),
            error_stacktrace="".join(traceback.format_exception(type(error), error, error.__traceback__)),
            metadata=metadata or {}
        )

    @staticmethod
    def create_task_started_event(context: AuditTaskContext) -> AuditEvent:
        return AuditEvent(
            event_type=AuditEventType.TASK_STARTED,
            pipeline_name=context.pipeline_name,
            pipeline_id=context.pipeline_id,
            task_name=context.task_name,
            task_id=context.task_id,
            task_attempt=context.task_attempt,
            status=AuditStatus.STARTED,
            **asdict(context.metrics)
        )

    @staticmethod
    def create_task_completed_event(context: AuditTaskContext, duration_ms: int) -> AuditEvent:
        event_data = asdict(context.metrics)
        event_data["duration_ms"] = duration_ms

        return AuditEvent(
            event_type=AuditEventType.TASK_COMPLETED,
            pipeline_name=context.pipeline_name,
            pipeline_id=context.pipeline_id,
            task_name=context.task_name,
            task_id=context.task_id,
            task_attempt=context.task_attempt,
            status=AuditStatus.SUCCEEDED,
            **event_data
        )

    @staticmethod
    def create_task_failed_event(context: AuditTaskContext, duration_ms: int, error: Exception) -> AuditEvent:
        event_data = asdict(context.metrics)
        event_data.update(
            duration_ms=duration_ms,
            error_type=type(error).__name__,
            error_message=str(error),
            error_stacktrace="".join(traceback.format_exception(type(error), error, error.__traceback__))
        )

        return AuditEvent(
            event_type=AuditEventType.TASK_FAILED,
            pipeline_name=context.pipeline_name,
            pipeline_id=context.pipeline_id,
            task_name=context.task_name,
            task_id=context.task_id,
            task_attempt=context.task_attempt,
            status=AuditStatus.FAILED,
            **event_data
        )

    @staticmethod
    def create_dataset_read_event(
            source_system: str,
            source_uri: str,
            row_count: int,
            pipeline_name: str | None = None,
            pipeline_id: str | None = None,
            metadata: dict | None = None
    ) -> AuditEvent:
        return AuditEvent(
            event_type=AuditEventType.DATASET_READ,
            pipeline_name=pipeline_name,
            pipeline_id=pipeline_id,
            status=AuditStatus.SUCCEEDED,
            source_system=source_system,
            source_uri=source_uri,
            input_row_count=row_count,
            metadata=metadata or {}
        )

    @staticmethod
    def create_dataset_written_event(
            source_system: str,
            source_uri: str,
            destination_system: str,
            destination_uri: str,
            row_count: int,
            pipeline_name: str | None = None,
            pipeline_id: str | None = None,
            metadata: dict | None = None
    ) -> AuditEvent:
        return AuditEvent(
            event_type=AuditEventType.DATASET_WRITTEN,
            pipeline_name=pipeline_name,
            pipeline_id=pipeline_id,
            status=AuditStatus.SUCCEEDED,
            source_system=source_system,
            source_uri=source_uri,
            destination_system=destination_system,
            destination_uri=destination_uri,
            output_row_count=row_count,
            metadata=metadata or {}
        )