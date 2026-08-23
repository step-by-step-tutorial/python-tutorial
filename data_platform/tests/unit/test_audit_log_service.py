from data_platform.audit.audit_event_factory import AuditEventFactory
from data_platform.audit.audit_event_factory import PipelineStartedAuditRequest
from data_platform.audit.audit_log_service import AuditLogService


class TestAuditLogService:

    def test_should_log_audit_event_to_console(self, mocker) -> None:
        given_event = AuditEventFactory.create_pipeline_started_event(
            PipelineStartedAuditRequest(
                pipeline_name="sale_pipeline",
                pipeline_id="pipeline-001",
            )
        )
        mock_logger_info = mocker.patch("data_platform.audit.audit_log_service.logger.info")

        AuditLogService().save(given_event)

        assert mock_logger_info.call_count == 1
        assert mock_logger_info.call_args.args[0] == "Audit event: %s"
