import time
from uuid import uuid4

from audit.audit_database_service import AuditDatabaseService
from audit.audit_event_factory import AuditEventFactory
from audit.audit_log_service import AuditLogService
from audit.audit_streaming_service import AuditStreamingService
from model.audit_metrics import AuditMetrics
from model.audit_task_context import AuditTaskContext
from util.time_utils import elapsed_milliseconds


class AuditService:

    def __init__(self) -> None:
        self.database = AuditDatabaseService()
        self.streaming = AuditStreamingService()
        self.log = AuditLogService()

    def start_pipeline(self, pipeline_name: str, pipeline_id: str, metadata: dict | None = None) -> float:
        started_at = time.perf_counter()
        event = AuditEventFactory.create_pipeline_started_event(pipeline_name, pipeline_id, metadata)

        self.database.save(event)
        self.streaming.publish(event)
        self.log.log(event)

        return started_at

    def complete_pipeline(
            self,
            pipeline_name: str,
            pipeline_id: str,
            started_at: float,
            input_row_count: int | None = None,
            output_row_count: int | None = None,
            rejected_row_count: int | None = None,
            metadata: dict | None = None
    ) -> None:
        event = AuditEventFactory.create_pipeline_completed_event(
            pipeline_name=pipeline_name,
            pipeline_id=pipeline_id,
            duration_ms=elapsed_milliseconds(started_at),
            input_row_count=input_row_count,
            output_row_count=output_row_count,
            rejected_row_count=rejected_row_count,
            metadata=metadata
        )

        self.database.save(event)
        self.streaming.publish(event)
        self.streaming.flush()
        self.log.log(event)

    def fail_pipeline(self, pipeline_name: str, pipeline_id: str, started_at: float, error: Exception, metadata: dict | None = None) -> None:
        event = AuditEventFactory.create_pipeline_failed_event(
            pipeline_name=pipeline_name,
            pipeline_id=pipeline_id,
            duration_ms=elapsed_milliseconds(started_at),
            error=error,
            metadata=metadata
        )

        self.database.save(event)
        self.streaming.publish(event)
        self.streaming.flush()
        self.log.log(event)

    def start_task(self, pipeline_name: str, pipeline_id: str, task_name: str, task_attempt: int, metrics: AuditMetrics) -> tuple[AuditTaskContext, float]:
        started_at = time.perf_counter()

        context = AuditTaskContext(
            pipeline_name=pipeline_name,
            pipeline_id=pipeline_id,
            task_name=task_name,
            task_id=str(uuid4()),
            task_attempt=task_attempt,
            metrics=metrics
        )

        event = AuditEventFactory.create_task_started_event(context)

        self.database.save(event)
        self.streaming.publish(event)
        self.log.log(event)

        return context, started_at

    def complete_task(self, context: AuditTaskContext, started_at: float) -> None:
        event = AuditEventFactory.create_task_completed_event(context, elapsed_milliseconds(started_at))

        self.database.save(event)
        self.streaming.publish(event)
        self.log.log(event)

    def fail_task(self, context: AuditTaskContext, started_at: float, error: Exception) -> None:
        event = AuditEventFactory.create_task_failed_event(context, elapsed_milliseconds(started_at), error)

        self.database.save(event)
        self.streaming.publish(event)
        self.log.log(event)

    def read_dataset(
            self,
            source_system: str,
            source_uri: str,
            row_count: int,
            pipeline_name: str | None = None,
            pipeline_id: str | None = None,
            metadata: dict | None = None
    ) -> None:
        event = AuditEventFactory.create_dataset_read_event(
            source_system=source_system,
            source_uri=source_uri,
            row_count=row_count,
            pipeline_name=pipeline_name,
            pipeline_id=pipeline_id,
            metadata=metadata
        )

        self.database.save(event)
        self.streaming.publish(event)
        self.log.log(event)

    def write_dataset(
            self,
            source_system: str,
            source_uri: str,
            destination_system: str,
            destination_uri: str,
            row_count: int,
            pipeline_name: str | None = None,
            pipeline_id: str | None = None,
            metadata: dict | None = None
    ) -> None:
        event = AuditEventFactory.create_dataset_written_event(
            source_system=source_system,
            source_uri=source_uri,
            destination_system=destination_system,
            destination_uri=destination_uri,
            row_count=row_count,
            pipeline_name=pipeline_name,
            pipeline_id=pipeline_id,
            metadata=metadata
        )

        self.database.save(event)
        self.streaming.publish(event)
        self.log.log(event)