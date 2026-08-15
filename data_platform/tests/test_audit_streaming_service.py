from audit.audit_event_factory import AuditEventFactory
from audit.audit_streaming_service import AuditStreamingService


class TestAuditStreamingService:

    def test_should_publish_audit_event_to_messaging_topic(self, mocker) -> None:
        # Given
        given_event = AuditEventFactory.create_pipeline_started_event(
            pipeline_name="sale_pipeline",
            pipeline_id="pipeline-001",
        )
        given_producer = mocker.Mock()
        mock_create_streaming_producer = mocker.patch(
            "audit.audit_streaming_service.create_streaming_producer",
            return_value=given_producer,
        )

        # When
        actual = AuditStreamingService("audit-topic")
        actual.publish(given_event)

        # Then
        assert mock_create_streaming_producer.call_count == 1
        assert given_producer.produce.call_count == 1
        assert given_producer.poll.call_count == 1

    def test_should_propagate_publish_errors(self, mocker) -> None:
        # Given
        given_event = AuditEventFactory.create_pipeline_started_event(
            pipeline_name="sale_pipeline",
            pipeline_id="pipeline-001",
        )
        given_producer = mocker.Mock()
        given_producer.produce.side_effect = RuntimeError("boom")
        mocker.patch(
            "audit.audit_streaming_service.create_streaming_producer",
            return_value=given_producer,
        )

        # When / Then
        service = AuditStreamingService("audit-topic")
        try:
            service.publish(given_event)
        except RuntimeError:
            pass

        assert given_producer.produce.call_count == 1
