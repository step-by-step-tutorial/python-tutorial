import traceback

from model.audit_event import AuditEventType, AuditStatus, AuditEvent
from streaming.audit_event_producer import AuditEventProducer


class AuditPipelineService:
    def __init__(self) -> None:
        self.producer = AuditEventProducer()

    def pipeline_started(self, pipeline_name: str, pipeline_id: str, metadata: dict | None = None) -> AuditEvent:
        event = AuditEvent(
            event_type=AuditEventType.PIPELINE_STARTED,
            pipeline_name=pipeline_name,
            pipeline_id=pipeline_id,
            status=AuditStatus.STARTED,
            metadata=metadata or {}
        )
        self.producer.publish(event)
        return event

    def pipeline_completed(
            self,
            pipeline_name: str,
            pipeline_id: str,
            input_row_count: int | None = None,
            output_row_count: int | None = None,
            rejected_row_count: int | None = None,
            duration_ms: int | None = None,
            metadata: dict | None = None
    ) -> None:
        self.producer.publish(
            AuditEvent(
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
        )

    def pipeline_failed(
            self,
            pipeline_name: str,
            pipeline_id: str,
            error: Exception,
            duration_ms: int | None = None,
            metadata: dict | None = None
    ) -> None:
        self.producer.publish(
            AuditEvent(
                event_type=AuditEventType.PIPELINE_FAILED,
                pipeline_name=pipeline_name,
                pipeline_id=pipeline_id,
                status=AuditStatus.FAILED,
                duration_ms=duration_ms,
                error_type=type(error).__name__,
                error_message=str(error),
                error_stacktrace=traceback.format_exc(),
                metadata=metadata or {}
            )
        )
