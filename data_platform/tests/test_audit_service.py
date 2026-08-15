from audit.audit_service import AuditService
from dataset.definition import Audit


class TestAuditService:

    def test_should_dispatch_pipeline_events_to_all_audit_outputs(self, mocker) -> None:
        # Given
        mock_database_service_class = mocker.patch("audit.audit_service.AuditDatabaseService")
        mock_streaming_service_class = mocker.patch("audit.audit_service.AuditStreamingService")
        mock_log_service_class = mocker.patch("audit.audit_service.AuditLogService")
        mock_save_event = mocker.patch("audit.audit_service.audit_archive_service.save_event")
        mock_elapsed_milliseconds = mocker.patch("audit.audit_service.elapsed_milliseconds", return_value=42)
        mocker.patch("audit.audit_service.time.perf_counter", return_value=100.0)

        given_database_service = mock_database_service_class.return_value
        given_streaming_service = mock_streaming_service_class.return_value
        given_streaming_service.producer = mocker.Mock()
        given_log_service = mock_log_service_class.return_value

        given_service = AuditService(Audit(topic="audit-topic", archive_enabled=True))

        # When
        actual_started_at = given_service.start_pipeline("sale_pipeline", "pipeline-001")
        given_service.complete_pipeline("sale_pipeline", "pipeline-001", started_at=100.0)
        given_service.fail_pipeline("sale_pipeline", "pipeline-001", started_at=100.0, error=RuntimeError("boom"))

        # Then
        assert actual_started_at == 100.0
        assert mock_database_service_class.call_count == 1
        assert mock_streaming_service_class.call_count == 1
        assert mock_log_service_class.call_count == 1
        assert mock_elapsed_milliseconds.call_count == 2
        assert given_database_service.save.call_count == 3
        assert given_streaming_service.publish.call_count == 3
        assert given_streaming_service.producer.flush.call_count == 2
        assert given_log_service.log.call_count == 3
        assert mock_save_event.call_count == 2

    def test_should_dispatch_task_and_dataset_events(self, mocker) -> None:
        # Given
        mock_database_service_class = mocker.patch("audit.audit_service.AuditDatabaseService")
        mock_streaming_service_class = mocker.patch("audit.audit_service.AuditStreamingService")
        mock_log_service_class = mocker.patch("audit.audit_service.AuditLogService")
        mock_save_event = mocker.patch("audit.audit_service.audit_archive_service.save_event")
        mock_elapsed_milliseconds = mocker.patch("audit.audit_service.elapsed_milliseconds", return_value=7)
        mocker.patch("audit.audit_service.time.perf_counter", return_value=200.0)
        mocker.patch("audit.audit_service.uuid4", return_value="task-001")

        given_database_service = mock_database_service_class.return_value
        given_streaming_service = mock_streaming_service_class.return_value
        given_streaming_service.producer = mocker.Mock()
        given_log_service = mock_log_service_class.return_value

        given_service = AuditService(Audit(topic="audit-topic", archive_enabled=True))

        # When
        actual_task_id, actual_started_at = given_service.start_task(
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
            started_at=200.0,
        )
        given_service.fail_task(
            "sale_pipeline",
            "pipeline-001",
            "populate_database",
            task_id=actual_task_id,
            task_attempt=1,
            started_at=200.0,
            error=RuntimeError("boom"),
        )
        given_service.read_dataset("datalake", "s3://bucket/path", 10)
        given_service.write_dataset("datalake", "s3://bucket/path", "database", "jdbc:postgresql://db/sale", 9)

        # Then
        assert actual_task_id == "task-001"
        assert actual_started_at == 200.0
        assert mock_database_service_class.call_count == 1
        assert mock_streaming_service_class.call_count == 1
        assert mock_log_service_class.call_count == 1
        assert mock_elapsed_milliseconds.call_count == 2
        assert given_database_service.save.call_count == 5
        assert given_streaming_service.publish.call_count == 5
        assert given_streaming_service.producer.flush.call_count == 0
        assert given_log_service.log.call_count == 5
        assert mock_save_event.call_count == 5
