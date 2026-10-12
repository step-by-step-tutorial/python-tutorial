from data_platform.model.audit_request_model import PipelineStartedAuditRequestModel
from data_platform.audit.audit_log_service import AuditLogService
from data_platform.model.audit_event_model import AuditEventModel


class TestAuditLogService:

    def test_should_log_audit_event_to_console(self, mocker) -> None:
        given_event = AuditEventModel.from_pipeline_started(
            PipelineStartedAuditRequestModel(
                pipeline_name="house_pipeline",
                pipeline_id="pipeline-001",
            )
        )
        mock_logger_info = mocker.patch("data_platform.audit.audit_log_service.logger.info")

        AuditLogService().save(given_event)

        assert mock_logger_info.call_count == 1
        assert mock_logger_info.call_args.args[0] == "Audit event: %s"


