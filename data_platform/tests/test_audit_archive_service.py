from datetime import UTC, datetime

from audit.audit_archive_service import AuditArchiveService
from audit.audit_event_factory import AuditEventFactory
from audit.audit_event_factory import PipelineStartedAuditRequest
from dataset.definition import AuditEndpoint


class TestAuditArchiveService:

    def test_should_save_audit_event_to_object_storage(self, mocker) -> None:
        # Given
        given_event = AuditEventFactory.create_pipeline_started_event(
            PipelineStartedAuditRequest(
                pipeline_name="sale_pipeline",
                pipeline_id="pipeline-001",
            )
        )
        given_event.event_time = datetime(2026, 8, 15, 12, 0, tzinfo=UTC)
        given_connection = mocker.Mock()
        mock_create_connection = mocker.patch(
            "audit.audit_archive_service.get_connection",
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

        actual = AuditArchiveService(given_endpoint).write(given_event)

        # Then
        assert actual is None
        assert mock_create_connection.call_count == 1
        assert mock_create_connection.call_args.args[0] == "audit.datalake"
        assert given_connection.put_object.call_count == 1

    def test_should_save_manifest_to_object_storage(self, mocker) -> None:
        # Given
        given_connection = mocker.Mock()
        mock_create_connection = mocker.patch(
            "audit.audit_archive_service.get_connection",
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
            pipeline_name="sale_pipeline",
            pipeline_id="pipeline-001",
            manifest={"rows": 10},
            event_time=datetime(2026, 8, 15, 12, 0, tzinfo=UTC),
        )

        # Then
        assert actual.startswith("s3a://app-datalake-audit/manifests/event_date=2026-08-15")
        assert mock_create_connection.call_count == 1
        assert mock_create_connection.call_args.args[0] == "audit.datalake"
        assert given_connection.put_object.call_count == 1
