import pytest

from audit.audit_event_factory import AuditEventFactory
from audit.audit_streaming_service import AuditStreamingService

pytestmark = pytest.mark.unit


class TestAuditStreamingService:

    def test_should_publish_audit_event_to_messaging_topic(self, mocker) -> None:
        # Given
        given_event = AuditEventFactory.create_pipeline_started_event(
            pipeline_name="sale_pipeline",
            pipeline_id="pipeline-001",
        )
        given_producer = mocker.Mock()

        # When
        actual = AuditStreamingService("audit-topic", producer=given_producer)
        actual.publish(given_event)

        # Then
        assert given_producer.produce.call_count == 1
        assert given_producer.poll.call_count == 1
        assert given_producer.produce.call_args.kwargs["key"] == str(given_event.event_id)

    def test_should_propagate_publish_errors(self, mocker) -> None:
        # Given
        given_event = AuditEventFactory.create_pipeline_started_event(
            pipeline_name="sale_pipeline",
            pipeline_id="pipeline-001",
        )
        given_producer = mocker.Mock()
        given_producer.produce.side_effect = RuntimeError("boom")
        service = AuditStreamingService("audit-topic", producer=given_producer)

        # When / Then
        try:
            service.publish(given_event)
        except RuntimeError:
            pass

        assert given_producer.produce.call_count == 1

    def test_should_lazily_create_producer_only_on_publish(self, mocker) -> None:
        given_producer = mocker.Mock()
        mock_create_producer = mocker.patch("connector.messaging.kafka_connector.create_producer", return_value=given_producer)

        service = AuditStreamingService("audit-topic")

        assert mock_create_producer.call_count == 0

        service.publish(AuditEventFactory.create_pipeline_started_event("sale_pipeline", "pipeline-001"))

        assert mock_create_producer.call_count == 1
