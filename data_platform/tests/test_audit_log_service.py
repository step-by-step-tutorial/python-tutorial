from audit.audit_event_factory import AuditEventFactory
from audit.audit_log_service import AuditLogService


class TestAuditLogService:

    def test_should_log_audit_event_identifier(self, mocker) -> None:
        # Given
        given_event = AuditEventFactory.create_pipeline_started_event(
            pipeline_name="sale_pipeline",
            pipeline_id="pipeline-001",
        )
        mock_logger_info = mocker.patch("audit.audit_log_service.logger.info")

        # When
        AuditLogService().log(given_event)

        # Then
        assert mock_logger_info.call_count == 1
