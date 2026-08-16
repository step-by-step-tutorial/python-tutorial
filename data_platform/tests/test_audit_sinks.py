from audit.sinks import ArchiveAuditSink, DatabaseAuditSink, LogAuditSink, StreamingAuditSink
from audit.audit_event_factory import AuditEventFactory
from audit.audit_database_service import AuditDatabaseService
from audit.audit_streaming_service import AuditStreamingService


class TestAuditSinks:

    def test_database_sink_should_delegate_to_audit_database_service(self, mocker) -> None:
        given_event = AuditEventFactory.create_pipeline_started_event("sale_pipeline", "pipeline-001")
        given_service = mocker.Mock(spec=AuditDatabaseService)

        DatabaseAuditSink(topic="audit-topic", service=given_service).write(given_event)

        assert given_service.save.call_count == 1
        assert given_service.save.call_args.args[1] == "audit-topic"

    def test_streaming_sink_should_delegate_to_audit_streaming_service(self, mocker) -> None:
        given_event = AuditEventFactory.create_pipeline_started_event("sale_pipeline", "pipeline-001")
        given_service = mocker.Mock(spec=AuditStreamingService)

        StreamingAuditSink(service=given_service).write(given_event)

        assert given_service.publish.call_count == 1

    def test_log_sink_should_log_event_identifier(self, mocker) -> None:
        given_event = AuditEventFactory.create_pipeline_started_event("sale_pipeline", "pipeline-001")
        mock_logger_info = mocker.patch("audit.sinks.logger.info")

        LogAuditSink().write(given_event)

        assert mock_logger_info.call_count == 1

    def test_archive_sink_should_respect_enabled_flag(self, mocker) -> None:
        given_event = AuditEventFactory.create_pipeline_started_event("sale_pipeline", "pipeline-001")
        mocker.patch("audit.sinks.audit_archive_service")
        mock_save_event = mocker.patch("audit.sinks.audit_archive_service.save_event")

        ArchiveAuditSink(bucket_name="audit-bucket", enabled=True).write(given_event)
        ArchiveAuditSink(bucket_name="audit-bucket", enabled=False).write(given_event)

        assert mock_save_event.call_count == 1
