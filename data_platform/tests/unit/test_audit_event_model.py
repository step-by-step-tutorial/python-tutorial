from data_platform.model.audit_request_model import DatasetReadAuditRequestModel
from data_platform.model.audit_request_model import DatasetWrittenAuditRequestModel
from data_platform.model.audit_request_model import PipelineCompletedAuditRequestModel
from data_platform.model.audit_request_model import PipelineFailedAuditRequestModel
from data_platform.model.audit_request_model import PipelineStartedAuditRequestModel
from data_platform.model.audit_request_model import TaskCompletedAuditRequestModel
from data_platform.model.audit_request_model import TaskFailedAuditRequestModel
from data_platform.model.audit_request_model import TaskStartedAuditRequestModel
from data_platform.model.audit_event_model import AuditEventModel, AuditEventType, AuditStatus


class TestAuditEventModel:

    def test_should_create_pipeline_events(self) -> None:
        # When
        given_started = AuditEventModel.from_pipeline_started(
            PipelineStartedAuditRequestModel(
                pipeline_name="house_pipeline",
                pipeline_id="pipeline-001",
                metadata={"dag_id": "dag-001"},
            )
        )
        given_completed = AuditEventModel.from_pipeline_completed(
            PipelineCompletedAuditRequestModel(
                pipeline_name="house_pipeline",
                pipeline_id="pipeline-001",
                duration_ms=42,
                input_row_count=10,
                output_row_count=9,
                rejected_row_count=1,
                metadata={"dag_id": "dag-001"},
            )
        )
        given_failed = AuditEventModel.from_pipeline_failed(
            PipelineFailedAuditRequestModel(
                pipeline_name="house_pipeline",
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
        given_task_started = AuditEventModel.from_task_started(
            TaskStartedAuditRequestModel(
                pipeline_name="house_pipeline",
                pipeline_id="pipeline-001",
                task_name="expose_database",
                task_id="task-001",
                task_attempt=1,
            )
        )
        given_task_completed = AuditEventModel.from_task_completed(
            TaskCompletedAuditRequestModel(
                pipeline_name="house_pipeline",
                pipeline_id="pipeline-001",
                task_name="expose_database",
                task_id="task-001",
                task_attempt=1,
                duration_ms=42,
                source_system="datalake",
                destination_system="database",
            )
        )
        given_task_failed = AuditEventModel.from_task_failed(
            TaskFailedAuditRequestModel(
                pipeline_name="house_pipeline",
                pipeline_id="pipeline-001",
                task_name="expose_database",
                task_id="task-001",
                task_attempt=1,
                duration_ms=42,
                error=RuntimeError("boom"),
            )
        )
        given_dataset_read = AuditEventModel.from_dataset_read(
            DatasetReadAuditRequestModel(
                source_system="datalake",
                source_uri="s3://bucket/path",
                row_count=10,
                pipeline_name="house_pipeline",
                pipeline_id="pipeline-001",
            )
        )
        given_dataset_written = AuditEventModel.from_dataset_written(
            DatasetWrittenAuditRequestModel(
                source_system="datalake",
                source_uri="s3://bucket/path",
                destination_system="database",
                destination_uri="jdbc:postgresql://db/house",
                row_count=9,
                pipeline_name="house_pipeline",
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


