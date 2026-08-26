from data_platform.audit.audit_database_service import AuditDatabaseService
from data_platform.audit.audit_event_factory import AuditEventFactory
from data_platform.audit.audit_event_factory import PipelineStartedAuditRequest
from data_platform.model.endpoints import AuditEndpoint


class TestAuditDatabaseService:

    def test_should_save_audit_event_to_single_table(self, mocker) -> None:
        # Given
        given_event = AuditEventFactory.create_pipeline_started_event(
            PipelineStartedAuditRequest(
                pipeline_name="house_pipeline",
                pipeline_id="pipeline-001",
                metadata={"airflow_dag_id": "dag-001"},
            )
        )

        given_connection = mocker.Mock()
        given_transaction_context = mocker.MagicMock()
        given_transaction_context.__enter__.return_value = given_connection
        given_connection.begin.return_value = given_transaction_context

        mock_create_connection = mocker.patch(
            "data_platform.audit.audit_database_service.connection_registry.get_item",
            return_value=given_connection
        )
        mock_read_text_file = mocker.patch(
            "data_platform.audit.audit_database_service.read_text_file",
            return_value="insert into audit.event values (:event_id)"
        )

        # When
        given_endpoint = AuditEndpoint(
            database_connection_name="audit.database",
            messaging_connection_name="audit.kafka.producer",
            datalake_connection_name="audit.datalake",
            create_sql_files={"create": "database/audit/create_tables.sql"},
            write_sql_files={"write": "database/audit/insert_event.sql"},
        )
        service = AuditDatabaseService(given_endpoint)
        service.save(given_event)

        # Then
        assert mock_create_connection.call_count == 1
        assert mock_create_connection.call_args.args[0] == "audit.database"
        assert mock_read_text_file.call_count == 1
        assert mock_read_text_file.call_args.args[0] == "database/audit/insert_event.sql"
        assert given_connection.begin.call_count == 1
        assert given_transaction_context.__enter__.call_count == 1
        assert given_transaction_context.__exit__.call_count == 1
        assert given_connection.execute.call_count == 1


