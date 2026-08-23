from data_platform.audit.audit_event_factory import AuditEventFactory
from data_platform.audit.audit_event_factory import DatasetReadAuditRequest
from data_platform.audit.audit_event_factory import DatasetWrittenAuditRequest
from data_platform.audit.audit_event_factory import PipelineCompletedAuditRequest
from data_platform.audit.audit_event_factory import PipelineFailedAuditRequest
from data_platform.audit.audit_event_factory import PipelineStartedAuditRequest
from data_platform.audit.audit_event_factory import TaskCompletedAuditRequest
from data_platform.audit.audit_event_factory import TaskFailedAuditRequest
from data_platform.audit.audit_event_factory import TaskStartedAuditRequest
from data_platform.audit.audit_event import AuditEventType, AuditStatus


class TestAuditEventFactory:

    def test_should_create_pipeline_events(self) -> None:
        # When
        given_started = AuditEventFactory.create_pipeline_started_event(
            PipelineStartedAuditRequest(
                pipeline_name="sale_pipeline",
                pipeline_id="pipeline-001",
                metadata={"dag_id": "dag-001"},
            )
        )
        given_completed = AuditEventFactory.create_pipeline_completed_event(
            PipelineCompletedAuditRequest(
                pipeline_name="sale_pipeline",
                pipeline_id="pipeline-001",
                duration_ms=42,
                input_row_count=10,
                output_row_count=9,
                rejected_row_count=1,
                metadata={"dag_id": "dag-001"},
            )
        )
        given_failed = AuditEventFactory.create_pipeline_failed_event(
            PipelineFailedAuditRequest(
                pipeline_name="sale_pipeline",
                pipeline_id="pipeline-001",
                duration_ms=42,
                error=RuntimeError("boom"),
            )
        )

        # Then
        assert given_started.event_type is AuditEventType.PIPELINE_STARTED
        assert given_started.status is AuditStatus.STARTED
        assert given_completed.event_type is AuditEventType.PIPELINE_COMPLETED
        assert given_completed.status is AuditStatus.SUCCEEDED
        assert given_failed.event_type is AuditEventType.PIPELINE_FAILED
        assert given_failed.status is AuditStatus.FAILED

    def test_should_create_task_and_dataset_events(self) -> None:
        # When
        given_task_started = AuditEventFactory.create_task_started_event(
            TaskStartedAuditRequest(
                pipeline_name="sale_pipeline",
                pipeline_id="pipeline-001",
                task_name="populate_database",
                task_id="task-001",
                task_attempt=1,
            )
        )
        given_task_completed = AuditEventFactory.create_task_completed_event(
            TaskCompletedAuditRequest(
                pipeline_name="sale_pipeline",
                pipeline_id="pipeline-001",
                task_name="populate_database",
                task_id="task-001",
                task_attempt=1,
                duration_ms=42,
                source_system="datalake",
                destination_system="database",
            )
        )
        given_task_failed = AuditEventFactory.create_task_failed_event(
            TaskFailedAuditRequest(
                pipeline_name="sale_pipeline",
                pipeline_id="pipeline-001",
                task_name="populate_database",
                task_id="task-001",
                task_attempt=1,
                duration_ms=42,
                error=RuntimeError("boom"),
            )
        )
        given_dataset_read = AuditEventFactory.create_dataset_read_event(
            DatasetReadAuditRequest(
                source_system="datalake",
                source_uri="s3://bucket/path",
                row_count=10,
                pipeline_name="sale_pipeline",
                pipeline_id="pipeline-001",
            )
        )
        given_dataset_written = AuditEventFactory.create_dataset_written_event(
            DatasetWrittenAuditRequest(
                source_system="datalake",
                source_uri="s3://bucket/path",
                destination_system="database",
                destination_uri="jdbc:postgresql://db/sale",
                row_count=9,
                pipeline_name="sale_pipeline",
                pipeline_id="pipeline-001",
            )
        )

        # Then
        assert given_task_started.event_type is AuditEventType.TASK_STARTED
        assert given_task_started.status is AuditStatus.STARTED
        assert given_task_completed.event_type is AuditEventType.TASK_COMPLETED
        assert given_task_completed.status is AuditStatus.SUCCEEDED
        assert given_task_failed.event_type is AuditEventType.TASK_FAILED
        assert given_task_failed.status is AuditStatus.FAILED
        assert given_dataset_read.event_type is AuditEventType.DATASET_READ
        assert given_dataset_written.event_type is AuditEventType.DATASET_WRITTEN
