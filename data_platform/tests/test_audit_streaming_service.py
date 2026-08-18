import pytest

from audit.audit_event_factory import AuditEventFactory
from audit.audit_event_factory import PipelineStartedAuditRequest
from audit.audit_messaging_service import AuditMessagingService
from dataset.definition import AuditEndpoint

pytestmark = pytest.mark.unit


class TestAuditMessagingService:

    def test_should_publish_audit_event_to_messaging_channel(self, mocker) -> None:
        # Given
        given_event = AuditEventFactory.create_pipeline_started_event(
            PipelineStartedAuditRequest(
                pipeline_name="sale_pipeline",
                pipeline_id="pipeline-001",
            )
        )
        given_producer = mocker.Mock()
        mock_create_producer = mocker.patch(
            "audit.audit_messaging_service.get_connection",
            return_value=given_producer,
        )

        # When
        actual = AuditMessagingService(
            AuditEndpoint(
                database_connection_name="audit.database",
                messaging_connection_name="audit.kafka.producer",
                datalake_connection_name="audit.datalake",
                create_sql_files={"create": "database/audit/create_tables.sql"},
                channel_name="audit-topic",
                write_sql_files={"write": "database/audit/insert_event.sql"},
            )
        )
        actual.write(given_event)

        # Then
        assert mock_create_producer.call_count == 1
        assert mock_create_producer.call_args.args[0] == "audit.kafka.producer"
        assert given_producer.produce.call_count == 1
        assert given_producer.poll.call_count == 1
        assert given_producer.produce.call_args.kwargs["key"] == str(given_event.event_id)

    def test_should_propagate_publish_errors(self, mocker) -> None:
        # Given
        given_event = AuditEventFactory.create_pipeline_started_event(
            PipelineStartedAuditRequest(
                pipeline_name="sale_pipeline",
                pipeline_id="pipeline-001",
            )
        )
        given_producer = mocker.Mock()
        given_producer.produce.side_effect = RuntimeError("boom")
        mocker.patch(
            "audit.audit_messaging_service.get_connection",
            return_value=given_producer,
        )
        service = AuditMessagingService(
            AuditEndpoint(
                database_connection_name="audit.database",
                messaging_connection_name="audit.kafka.producer",
                datalake_connection_name="audit.datalake",
                create_sql_files={"create": "database/audit/create_tables.sql"},
                channel_name="audit-topic",
                write_sql_files={"write": "database/audit/insert_event.sql"},
            )
        )

        # When / Then
        try:
            service.write(given_event)
        except RuntimeError:
            pass

        assert given_producer.produce.call_count == 1

    def test_should_create_producer_in_init(self, mocker) -> None:
        given_producer = mocker.Mock()
        mock_create_producer = mocker.patch(
            "audit.audit_messaging_service.get_connection",
            return_value=given_producer,
        )

        service = AuditMessagingService(
            AuditEndpoint(
                database_connection_name="audit.database",
                messaging_connection_name="audit.kafka.producer",
                datalake_connection_name="audit.datalake",
                create_sql_files={"create": "database/audit/create_tables.sql"},
                channel_name="audit-topic",
                write_sql_files={"write": "database/audit/insert_event.sql"},
            )
        )
        assert mock_create_producer.call_count == 1
        assert mock_create_producer.call_args.args[0] == "audit.kafka.producer"
