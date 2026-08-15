from audit.audit_service import AuditService
from dataset.definition import Audit
from model.audit_event import AuditEventType


class TestAuditService:

    def test_should_dispatch_events_to_injected_sinks(self, mocker) -> None:
        given_sink_1 = mocker.Mock()
        given_sink_2 = mocker.Mock()
        mocker.patch("audit.audit_service.time.perf_counter", return_value=100.0)
        mocker.patch("audit.audit_service.uuid4", return_value="task-001")

        given_service = AuditService(Audit(topic="audit-topic", archive_enabled=True), sinks=[given_sink_1, given_sink_2])

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
        assert given_sink_1.write.call_count == 8
        assert given_sink_2.write.call_count == 8

    def test_should_emit_pipeline_and_task_failure_events(self, mocker) -> None:
        given_sink = mocker.Mock()
        mocker.patch("audit.audit_service.time.perf_counter", return_value=100.0)
        mocker.patch("audit.audit_service.uuid4", return_value="task-001")

        given_service = AuditService(Audit(topic="audit-topic", archive_enabled=True), sinks=[given_sink])
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

        assert given_sink.write.call_count == 3
        assert given_sink.write.call_args_list[1].args[0].event_type == AuditEventType.TASK_FAILED
        assert given_sink.write.call_args_list[2].args[0].event_type == AuditEventType.PIPELINE_FAILED
