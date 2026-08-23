from data_platform.audit.audit_event_factory import DatasetReadAuditRequest
from data_platform.audit.audit_event_factory import DatasetWrittenAuditRequest
from data_platform.audit.audit_event_factory import PipelineCompletedAuditRequest
from data_platform.audit.audit_event_factory import PipelineFailedAuditRequest
from data_platform.audit.audit_event_factory import PipelineStartedAuditRequest
from data_platform.audit.audit_event_factory import TaskCompletedAuditRequest
from data_platform.audit.audit_event_factory import TaskFailedAuditRequest
from data_platform.audit.audit_event_factory import TaskStartedAuditRequest
from data_platform.audit.audit_event_factory import AuditEventFactory
from data_platform.audit.audit_service import AuditService
from data_platform.model import AuditEndpoint
from data_platform.model.audit_event import AuditEventType


class TestAuditService:

    def test_should_dispatch_events_to_concrete_services(self, mocker) -> None:
        given_database_service = mocker.Mock()
        given_messaging_service = mocker.Mock()
        given_archive_service = mocker.Mock()
        given_log_service = mocker.Mock()
        mock_log_service_ctor = mocker.patch(
            "data_platform.audit.audit_service.AuditLogService",
            return_value=given_log_service,
        )
        mock_database_service_ctor = mocker.patch(
            "data_platform.audit.audit_service.AuditDatabaseService",
            return_value=given_database_service,
        )
        mock_messaging_service_ctor = mocker.patch(
            "data_platform.audit.audit_service.AuditMessagingService",
            return_value=given_messaging_service,
        )
        mock_archive_service_ctor = mocker.patch(
            "data_platform.audit.audit_service.AuditArchiveService",
            return_value=given_archive_service,
        )

        given_service = AuditService(
            AuditEndpoint(
                database_connection_name="audit.database",
                messaging_connection_name="audit.kafka.producer",
                datalake_connection_name="audit.datalake",
                create_sql_files={"create": "database/audit/create_tables.sql"},
                channel_name="audit-topic",
                bucket_name="app-datalake-audit",
                write_sql_files={"write": "database/audit/insert_event.sql"},
            )
        )
        given_service.emit = mocker.Mock(wraps=given_service.emit)

        given_service.emit(
            AuditEventFactory.create_pipeline_started_event(
                PipelineStartedAuditRequest(
                    pipeline_name="sale_pipeline",
                    pipeline_id="pipeline-001",
                )
            )
        )
        actual_task_id = "task-001"
        given_service.emit(
            AuditEventFactory.create_task_started_event(
                TaskStartedAuditRequest(
                    pipeline_name="sale_pipeline",
                    pipeline_id="pipeline-001",
                    task_name="populate_database",
                    task_id=actual_task_id,
                    task_attempt=1,
                )
            )
        )
        given_service.emit(
            AuditEventFactory.create_task_completed_event(
                TaskCompletedAuditRequest(
                    pipeline_name="sale_pipeline",
                    pipeline_id="pipeline-001",
                    task_name="populate_database",
                    task_id=actual_task_id,
                    task_attempt=1,
                    duration_ms=0,
                )
            )
        )
        given_service.emit(
            AuditEventFactory.create_task_failed_event(
                TaskFailedAuditRequest(
                    pipeline_name="sale_pipeline",
                    pipeline_id="pipeline-001",
                    task_name="populate_database",
                    task_id=actual_task_id,
                    task_attempt=1,
                    duration_ms=0,
                    error=RuntimeError("boom"),
                )
            )
        )
        given_service.emit(
            AuditEventFactory.create_pipeline_completed_event(
                PipelineCompletedAuditRequest(
                    pipeline_name="sale_pipeline",
                    pipeline_id="pipeline-001",
                    duration_ms=0,
                )
            )
        )
        given_service.emit(
            AuditEventFactory.create_pipeline_failed_event(
                PipelineFailedAuditRequest(
                    pipeline_name="sale_pipeline",
                    pipeline_id="pipeline-001",
                    duration_ms=0,
                    error=RuntimeError("boom"),
                )
            )
        )
        given_service.emit(
            AuditEventFactory.create_dataset_read_event(
                DatasetReadAuditRequest(
                    source_system="datalake",
                    source_uri="s3://bucket/path",
                    row_count=10,
                )
            )
        )
        given_service.emit(
            AuditEventFactory.create_dataset_written_event(
                DatasetWrittenAuditRequest(
                    source_system="datalake",
                    source_uri="s3://bucket/path",
                    destination_system="database",
                    destination_uri="jdbc:postgresql://db/sale",
                    row_count=9,
                )
            )
        )

        assert actual_task_id == "task-001"
        assert mock_log_service_ctor.call_count == 1
        assert mock_database_service_ctor.call_args.args[0].database_connection_name == "audit.database"
        assert mock_database_service_ctor.call_args.args[0].write_sql_files == {"write": "database/audit/insert_event.sql"}
        assert mock_messaging_service_ctor.call_args.args[0].messaging_connection_name == "audit.kafka.producer"
        assert mock_messaging_service_ctor.call_args.args[0].channel_name == "audit-topic"
        assert mock_archive_service_ctor.call_args.args[0].datalake_connection_name == "audit.datalake"
        assert mock_archive_service_ctor.call_args.args[0].bucket_name == "app-datalake-audit"
        assert given_service.emit.call_count == 8
        assert given_log_service.write.call_count == 8
        assert given_database_service.write.call_count == 8
        assert given_messaging_service.write.call_count == 8
        assert given_archive_service.write.call_count == 8

    def test_should_write_to_archive_when_bucket_is_empty(self, mocker) -> None:
        given_database_service = mocker.Mock()
        given_messaging_service = mocker.Mock()
        given_archive_service = mocker.Mock()
        given_log_service = mocker.Mock()
        mocker.patch("data_platform.audit.audit_service.AuditLogService", return_value=given_log_service)
        mocker.patch("data_platform.audit.audit_service.AuditDatabaseService", return_value=given_database_service)
        mocker.patch("data_platform.audit.audit_service.AuditMessagingService", return_value=given_messaging_service)
        mocker.patch("data_platform.audit.audit_service.AuditArchiveService", return_value=given_archive_service)

        given_service = AuditService(
            AuditEndpoint(
                database_connection_name="audit.database",
                messaging_connection_name="audit.kafka.producer",
                datalake_connection_name="audit.datalake",
                create_sql_files={"create": "database/audit/create_tables.sql"},
                channel_name="audit-topic",
                bucket_name="",
                write_sql_files={"write": "database/audit/insert_event.sql"},
            )
        )
        given_service.emit = mocker.Mock(wraps=given_service.emit)
        given_service.emit(
            AuditEventFactory.create_pipeline_started_event(
                PipelineStartedAuditRequest(
                    pipeline_name="sale_pipeline",
                    pipeline_id="pipeline-001",
                )
            )
        )

        try:
            raise RuntimeError("boom")
        except RuntimeError as error:
            given_service.emit(
                AuditEventFactory.create_task_failed_event(
                    TaskFailedAuditRequest(
                        pipeline_name="sale_pipeline",
                        pipeline_id="pipeline-001",
                        task_name="populate_database",
                        task_id="task-001",
                        task_attempt=1,
                        duration_ms=0,
                        error=error,
                    )
                )
            )
            given_service.emit(
                AuditEventFactory.create_pipeline_failed_event(
                    PipelineFailedAuditRequest(
                        pipeline_name="sale_pipeline",
                        pipeline_id="pipeline-001",
                        duration_ms=0,
                        error=error,
                    )
                )
            )

        assert given_database_service.write.call_count == 3
        assert given_messaging_service.write.call_count == 3
        assert given_archive_service.write.call_count == 3
        assert given_log_service.write.call_count == 3
