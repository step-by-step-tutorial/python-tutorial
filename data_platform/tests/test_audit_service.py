from audit.audit_service import AuditService
from dataset.definition import AuditEndpoint
from model.audit_event import AuditEventType


class TestAuditService:

    def test_should_dispatch_events_to_concrete_services(self, mocker) -> None:
        given_database_service = mocker.Mock()
        given_messaging_service = mocker.Mock()
        given_archive_service = mocker.Mock()
        given_log_service = mocker.Mock()
        mocker.patch("audit.audit_service.time.perf_counter", return_value=100.0)
        mocker.patch("audit.audit_service.uuid4", return_value="task-001")
        mock_log_service_ctor = mocker.patch(
            "audit.audit_service.AuditLogService",
            return_value=given_log_service,
        )
        mock_database_service_ctor = mocker.patch(
            "audit.audit_service.AuditDatabaseService",
            return_value=given_database_service,
        )
        mock_messaging_service_ctor = mocker.patch(
            "audit.audit_service.AuditMessagingService",
            return_value=given_messaging_service,
        )
        mock_archive_service_ctor = mocker.patch(
            "audit.audit_service.AuditArchiveService",
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

        actual_started_at = given_service.start_pipeline("sale_pipeline", "pipeline-001")
        actual_task_id, actual_task_started_at = given_service.start_task(
            "sale_pipeline",
            "pipeline-001",
            "populate_database",
            task_attempt=1,
        )
        given_service.complete_task(
            "sale_pipeline",
            "pipeline-001",
            "populate_database",
            task_id=actual_task_id,
            task_attempt=1,
            started_at=actual_task_started_at,
        )
        given_service.fail_task(
            "sale_pipeline",
            "pipeline-001",
            "populate_database",
            task_id=actual_task_id,
            task_attempt=1,
            started_at=actual_task_started_at,
            error=RuntimeError("boom"),
        )
        given_service.complete_pipeline("sale_pipeline", "pipeline-001", started_at=actual_started_at)
        given_service.fail_pipeline("sale_pipeline", "pipeline-001", started_at=actual_started_at, error=RuntimeError("boom"))
        given_service.read_dataset("datalake", "s3://bucket/path", 10)
        given_service.write_dataset("datalake", "s3://bucket/path", "database", "jdbc:postgresql://db/sale", 9)

        assert actual_started_at == 100.0
        assert actual_task_started_at == 100.0
        assert actual_task_id == "task-001"
        assert mock_log_service_ctor.call_count == 1
        assert mock_database_service_ctor.call_args.args[0].database_connection_name == "audit.database"
        assert mock_database_service_ctor.call_args.args[0].write_sql_files == {"write": "database/audit/insert_event.sql"}
        assert mock_messaging_service_ctor.call_args.args[0].messaging_connection_name == "audit.kafka.producer"
        assert mock_messaging_service_ctor.call_args.args[0].channel_name == "audit-topic"
        assert mock_archive_service_ctor.call_args.args[0].datalake_connection_name == "audit.datalake"
        assert mock_archive_service_ctor.call_args.args[0].bucket_name == "app-datalake-audit"
        assert given_log_service.write.call_count == 8
        assert given_database_service.write.call_count == 8
        assert given_messaging_service.write.call_count == 8
        assert given_archive_service.write.call_count == 8

    def test_should_write_to_archive_when_bucket_is_empty(self, mocker) -> None:
        given_database_service = mocker.Mock()
        given_messaging_service = mocker.Mock()
        given_archive_service = mocker.Mock()
        given_log_service = mocker.Mock()
        mocker.patch("audit.audit_service.time.perf_counter", return_value=100.0)
        mocker.patch("audit.audit_service.uuid4", return_value="task-001")
        mocker.patch("audit.audit_service.AuditLogService", return_value=given_log_service)
        mocker.patch("audit.audit_service.AuditDatabaseService", return_value=given_database_service)
        mocker.patch("audit.audit_service.AuditMessagingService", return_value=given_messaging_service)
        mocker.patch("audit.audit_service.AuditArchiveService", return_value=given_archive_service)

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
        started_at = given_service.start_pipeline("sale_pipeline", "pipeline-001")

        try:
            raise RuntimeError("boom")
        except RuntimeError as error:
            given_service.fail_task(
                "sale_pipeline",
                "pipeline-001",
                "populate_database",
                task_id="task-001",
                task_attempt=1,
                started_at=started_at,
                error=error,
            )
            given_service.fail_pipeline("sale_pipeline", "pipeline-001", started_at=started_at, error=error)

        assert given_database_service.write.call_count == 3
        assert given_messaging_service.write.call_count == 3
        assert given_archive_service.write.call_count == 3
        assert given_log_service.write.call_count == 3
