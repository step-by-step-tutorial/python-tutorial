from datetime import UTC, datetime

from audit import audit_archive_service as system_under_test
from audit.audit_event_factory import AuditEventFactory


class TestAuditArchiveService:

    def test_should_save_audit_event_to_object_storage(self, mocker) -> None:
        # Given
        given_event = AuditEventFactory.create_pipeline_started_event(
            pipeline_name="sale_pipeline",
            pipeline_id="pipeline-001",
        )
        given_event.event_time = datetime(2026, 8, 15, 12, 0, tzinfo=UTC)
        given_connection = mocker.Mock()
        given_context = mocker.MagicMock()
        given_context.__enter__.return_value = given_connection
        mock_create_connection = mocker.patch.object(
            system_under_test.datalake_connection_factory,
            "create_connection",
            return_value=given_context,
        )

        # When
        actual = system_under_test.save_event(given_event, bucket_name="app-datalake-audit")

        # Then
        assert actual.startswith("s3a://app-datalake-audit/events/event_date=2026-08-15")
        assert mock_create_connection.call_count == 1
        assert given_connection.put_object.call_count == 1

    def test_should_save_manifest_to_object_storage(self, mocker) -> None:
        # Given
        given_connection = mocker.Mock()
        given_context = mocker.MagicMock()
        given_context.__enter__.return_value = given_connection
        mock_create_connection = mocker.patch.object(
            system_under_test.datalake_connection_factory,
            "create_connection",
            return_value=given_context,
        )

        # When
        actual = system_under_test.save_manifest(
            pipeline_name="sale_pipeline",
            pipeline_id="pipeline-001",
            manifest={"rows": 10},
            event_time=datetime(2026, 8, 15, 12, 0, tzinfo=UTC),
            bucket_name="app-datalake-audit",
        )

        # Then
        assert actual.startswith("s3a://app-datalake-audit/manifests/event_date=2026-08-15")
        assert mock_create_connection.call_count == 1
        assert given_connection.put_object.call_count == 1
