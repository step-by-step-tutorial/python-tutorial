from audit.audit_database_service import AuditDatabaseService
from audit.audit_event_factory import AuditEventFactory


class TestAuditDatabaseService:

    def test_should_save_audit_event_to_single_table(self, mocker) -> None:
        # Given
        given_event = AuditEventFactory.create_pipeline_started_event(
            pipeline_name="sale_pipeline",
            pipeline_id="pipeline-001",
            metadata={"airflow_dag_id": "dag-001"}
        )

        given_connection = mocker.Mock()
        given_transaction_context = mocker.MagicMock()
        given_transaction_context.__enter__.return_value = given_connection
        given_connection.begin.return_value = given_transaction_context

        mock_create_connection = mocker.patch(
            "audit.audit_database_service.create_connection",
            return_value=given_connection
        )

        # When
        AuditDatabaseService().save(given_event)

        # Then
        assert mock_create_connection.call_count == 1
        assert given_connection.begin.call_count == 1
        assert given_transaction_context.__enter__.call_count == 1
        assert given_transaction_context.__exit__.call_count == 1
        assert given_connection.execute.call_count == 1

        _, actual_parameters = given_connection.execute.call_args.args

        assert actual_parameters["pipeline_id"] == "pipeline-001"
        assert actual_parameters["pipeline_name"] == "sale_pipeline"
        assert actual_parameters["streaming_topic"] is not None
        assert actual_parameters["metadata"] == '{"airflow_dag_id": "dag-001"}'
