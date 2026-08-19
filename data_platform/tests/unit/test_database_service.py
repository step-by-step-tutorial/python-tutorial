import pytest
import pandas as pd

from dataset.definition import AuditEndpoint, Dataframe, DatabaseEndpoint, Dataset, FileEndpoint
from persistence import database_repository as system_under_test


def build_dataset() -> Dataset:
    return Dataset(
        name="example",
        dataframe=Dataframe(schema=None, required_columns=frozenset()),
        audit=AuditEndpoint(
            database_connection_name="audit.database",
            messaging_connection_name="audit.kafka.producer",
            datalake_connection_name="audit.datalake",
            create_sql_files={"create": "database/audit/create_tables.sql"},
            write_sql_files={"write": "database/audit/insert_event.sql"},
        ),
        processors={},
        endpoints={
            "file": FileEndpoint(file_name="example.csv"),
            "database": DatabaseEndpoint(
                connection_name="sale.database",
                schema="sale",
                stage_table_name="example_stage",
                full_stage_table_name="sale.example_stage",
                table_names=["sale.example_stage"],
                create_sql_files={"create": "create.sql"},
                truncate_sql_files={"truncate": "before.sql"},
                write_sql_files={"after": "after.sql"},
                query_sql_files={},
            ),
        },
    )


class TestPopulateStageFromPandas:

    def test_should_populate_stage_table(self, mocker) -> None:
        given_database = build_dataset().get_endpoint("database", DatabaseEndpoint)
        given_dataframe = mocker.Mock(spec=pd.DataFrame)
        given_database_engine = mocker.Mock()
        given_database_connection = mocker.Mock()
        given_transaction_context = mocker.MagicMock()

        given_transaction_context.__enter__.return_value = given_database_connection
        given_database_engine.begin.return_value = given_transaction_context

        mock_create_connection = mocker.patch(
            "persistence.database_repository.get_connection",
            return_value=given_database_engine,
        )

        repository = system_under_test.DatabaseRepository(given_database)
        actual = repository.populate_stage_table_from_memory(given_dataframe)

        assert actual is None
        assert mock_create_connection.call_count == 1
        assert mock_create_connection.call_args.args[0] == "sale.database"
        assert given_database_engine.begin.call_count == 1
        assert given_transaction_context.__enter__.call_count == 1
        assert given_transaction_context.__exit__.call_count == 1
        assert given_dataframe.to_sql.call_count == 1
        assert given_dataframe.to_sql.call_args.kwargs["name"] == "example_stage"
        assert given_dataframe.to_sql.call_args.kwargs["schema"] == "sale"

    def test_should_propagate_error_when_population_fails(self, mocker) -> None:
        given_error_message = "Pandas stage population failed"
        given_database = build_dataset().get_endpoint("database", DatabaseEndpoint)
        given_dataframe = mocker.Mock(spec=pd.DataFrame)
        given_database_engine = mocker.Mock()
        given_transaction_context = mocker.MagicMock()

        given_database_engine.begin.return_value = given_transaction_context
        given_dataframe.to_sql.side_effect = RuntimeError(given_error_message)

        mocker.patch(
            "persistence.database_repository.get_connection",
            return_value=given_database_engine,
        )

        with pytest.raises(RuntimeError) as actual:
            system_under_test.DatabaseRepository(given_database).populate_stage_table_from_memory(given_dataframe)

        assert str(actual.value) == given_error_message


class TestPopulateStageFromSpark:

    def test_should_populate_stage_table(self, mocker) -> None:
        given_database = build_dataset().get_endpoint("database", DatabaseEndpoint)
        given_dataframe = mocker.Mock()
        given_writer = mocker.Mock()

        given_dataframe.write = given_writer
        given_writer.format.return_value = given_writer
        given_writer.option.return_value = given_writer
        given_writer.mode.return_value = given_writer

        actual = system_under_test.DatabaseRepository(given_database).populate_stage_table_from_spark(given_dataframe)

        assert actual is None
        assert given_writer.format.call_count == 1
        assert given_writer.option.call_count == 5
        assert given_writer.mode.call_count == 1
        assert given_writer.save.call_count == 1

    def test_should_propagate_error_when_population_fails(self, mocker) -> None:
        given_error_message = "Spark stage population failed"
        given_database = build_dataset().get_endpoint("database", DatabaseEndpoint)
        given_dataframe = mocker.Mock()
        given_writer = mocker.Mock()

        given_dataframe.write = given_writer
        given_writer.format.return_value = given_writer
        given_writer.option.return_value = given_writer
        given_writer.mode.return_value = given_writer
        given_writer.save.side_effect = RuntimeError(given_error_message)

        with pytest.raises(RuntimeError) as actual:
            system_under_test.DatabaseRepository(given_database).populate_stage_table_from_spark(given_dataframe)

        assert str(actual.value) == given_error_message


class TestPopulate:

    def test_should_run_pre_sql_stage_population_and_post_sql_for_pandas(self, mocker) -> None:
        given_database = build_dataset().get_endpoint("database", DatabaseEndpoint)
        given_dataframe = mocker.Mock(spec=pd.DataFrame)
        repository = system_under_test.DatabaseRepository(given_database)
        mock_run_sql_files = mocker.patch.object(repository, "run_sql_files")
        mock_populate_stage = mocker.patch.object(repository, "populate_stage_from_memory")

        repository.truncate_and_populate_from_memory(given_dataframe)

        assert mock_run_sql_files.call_count == 2
        assert mock_populate_stage.call_count == 1

    def test_should_run_pre_sql_stage_population_and_post_sql_for_spark(self, mocker) -> None:
        given_database = build_dataset().get_endpoint("database", DatabaseEndpoint)
        given_dataframe = mocker.Mock()
        repository = system_under_test.DatabaseRepository(given_database)
        mock_run_sql_files = mocker.patch.object(repository, "run_sql_files")
        mock_populate_stage = mocker.patch.object(repository, "populate_stage_from_spark")

        repository.truncate_and_populate_from_spark(given_dataframe)

        assert mock_run_sql_files.call_count == 2
        assert mock_populate_stage.call_count == 1
