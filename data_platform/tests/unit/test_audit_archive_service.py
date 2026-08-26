from datetime import UTC, datetime

from data_platform.audit.audit_archive_service import AuditArchiveService
from data_platform.audit.audit_event_factory import AuditEventFactory
from data_platform.audit.audit_event_factory import PipelineStartedAuditRequest
from data_platform.model.endpoints import AuditEndpoint


class TestAuditArchiveService:

    def test_should_save_audit_event_to_object_storage(self, mocker) -> None:
        # Given
        given_event = AuditEventFactory.create_pipeline_started_event(
            PipelineStartedAuditRequest(
                pipeline_name="house_pipeline",
                pipeline_id="pipeline-001",
            )
        )
        given_event.event_time = datetime(2026, 8, 15, 12, 0, tzinfo=UTC)
        given_connection = mocker.Mock()
        given_connection.list_buckets.return_value = {"Buckets": []}
        mock_create_connection = mocker.patch(
            "data_platform.audit.audit_archive_service.connection_registry.get_item",
            return_value=given_connection,
        )

        # When
        given_endpoint = AuditEndpoint(
            database_connection_name="audit.database",
            messaging_connection_name="audit.kafka.producer",
            datalake_connection_name="audit.datalake",
            create_sql_files={"create": "database/audit/create_tables.sql"},
            bucket_name="app-datalake-audit",
            write_sql_files={"write": "database/audit/insert_event.sql"},
        )

        actual = AuditArchiveService(given_endpoint).save(given_event)

        # Then
        assert actual is None
        assert mock_create_connection.call_count == 1
        assert mock_create_connection.call_args.args[0] == "audit.datalake"
        assert given_connection.list_buckets.call_count == 1
        assert given_connection.create_bucket.call_count == 1
        assert given_connection.put_object.call_count == 1

    def test_should_save_manifest_to_object_storage(self, mocker) -> None:
        # Given
        given_connection = mocker.Mock()
        given_connection.list_buckets.return_value = {"Buckets": []}
        mock_create_connection = mocker.patch(
            "data_platform.audit.audit_archive_service.connection_registry.get_item",
            return_value=given_connection,
        )

        # When
        given_endpoint = AuditEndpoint(
            database_connection_name="audit.database",
            messaging_connection_name="audit.kafka.producer",
            datalake_connection_name="audit.datalake",
            create_sql_files={"create": "database/audit/create_tables.sql"},
            bucket_name="app-datalake-audit",
            write_sql_files={"write": "database/audit/insert_event.sql"},
        )

        actual = AuditArchiveService(given_endpoint).write_manifest(
            pipeline_name="house_pipeline",
            pipeline_id="pipeline-001",
            manifest={"rows": 10},
            event_time=datetime(2026, 8, 15, 12, 0, tzinfo=UTC),
        )

        # Then
        assert actual.startswith("s3a://app-datalake-audit/manifests/event_date=2026-08-15")
        assert mock_create_connection.call_count == 1
        assert mock_create_connection.call_args.args[0] == "audit.datalake"
        assert given_connection.list_buckets.call_count == 1
        assert given_connection.create_bucket.call_count == 1
        assert given_connection.put_object.call_count == 1


