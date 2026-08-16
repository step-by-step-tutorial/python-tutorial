import pytest
import pandas as pd

from dataset.definition import Audit, Dataframe, DatabaseEndpoint, Dataset, FileEndpoint
from persistence.database import database_service as system_under_test


def build_dataset() -> Dataset:
    return Dataset(
        name="example",
        dataframe=Dataframe(schema=None, required_columns=frozenset()),
        audit=Audit(),
        processor_factories={},
        sources={
            "file": FileEndpoint(file_name="example.csv"),
        },
        destinations={
            "database": DatabaseEndpoint(
                table_name="sale.example_stage",
                preparing_sql_files=("before.sql",),
                analytical_sql_files=("after.sql",),
            ),
        },
    )


class TestPopulateStageFromPandas:

    def test_should_populate_stage_table(self, mocker) -> None:
        given_dataset = build_dataset()
        given_dataframe = mocker.Mock(spec=pd.DataFrame)
        given_database_engine = mocker.Mock()
        given_database_connection = mocker.Mock()
        given_transaction_context = mocker.MagicMock()

        given_transaction_context.__enter__.return_value = given_database_connection
        given_database_engine.begin.return_value = given_transaction_context

        mock_create_connection = mocker.patch.object(
            system_under_test.database_connection_factory,
            "create_connection",
            return_value=given_database_engine,
        )

        actual = system_under_test.populate_stage_from_pandas(given_dataset, given_dataframe)

        assert actual is None
        assert mock_create_connection.call_count == 1
        assert given_database_engine.begin.call_count == 1
        assert given_transaction_context.__enter__.call_count == 1
        assert given_transaction_context.__exit__.call_count == 1
        assert given_dataframe.to_sql.call_count == 1

    def test_should_propagate_error_when_population_fails(self, mocker) -> None:
        given_error_message = "Pandas stage population failed"
        given_dataset = build_dataset()
        given_dataframe = mocker.Mock(spec=pd.DataFrame)
        given_database_engine = mocker.Mock()
        given_transaction_context = mocker.MagicMock()

        given_database_engine.begin.return_value = given_transaction_context
        given_dataframe.to_sql.side_effect = RuntimeError(given_error_message)

        mocker.patch.object(
            system_under_test.database_connection_factory,
            "create_connection",
            return_value=given_database_engine,
        )

        with pytest.raises(RuntimeError) as actual:
            system_under_test.populate_stage_from_pandas(given_dataset, given_dataframe)

        assert str(actual.value) == given_error_message


class TestPopulateStageFromSpark:

    def test_should_populate_stage_table(self, mocker) -> None:
        given_dataset = build_dataset()
        given_dataframe = mocker.Mock()
        given_writer = mocker.Mock()

        given_dataframe.write = given_writer
        given_writer.format.return_value = given_writer
        given_writer.option.return_value = given_writer
        given_writer.mode.return_value = given_writer

        actual = system_under_test.populate_stage_from_spark(given_dataset, given_dataframe)

        assert actual is None
        assert given_writer.format.call_count == 1
        assert given_writer.option.call_count == 5
        assert given_writer.mode.call_count == 1
        assert given_writer.save.call_count == 1

    def test_should_propagate_error_when_population_fails(self, mocker) -> None:
        given_error_message = "Spark stage population failed"
        given_dataset = build_dataset()
        given_dataframe = mocker.Mock()
        given_writer = mocker.Mock()

        given_dataframe.write = given_writer
        given_writer.format.return_value = given_writer
        given_writer.option.return_value = given_writer
        given_writer.mode.return_value = given_writer
        given_writer.save.side_effect = RuntimeError(given_error_message)

        with pytest.raises(RuntimeError) as actual:
            system_under_test.populate_stage_from_spark(given_dataset, given_dataframe)

        assert str(actual.value) == given_error_message


class TestPopulate:

    def test_should_run_pre_sql_stage_population_and_post_sql_for_pandas(self, mocker) -> None:
        given_dataset = build_dataset()
        given_dataframe = mocker.Mock(spec=pd.DataFrame)
        mock_run_sql_files = mocker.patch.object(system_under_test, "run_sql_files")
        mock_populate_stage = mocker.patch.object(system_under_test, "populate_stage_from_pandas")

        system_under_test.truncate_and_populate_from_pandas(given_dataset, given_dataframe)

        assert mock_run_sql_files.call_count == 2
        assert mock_populate_stage.call_count == 1

    def test_should_run_pre_sql_stage_population_and_post_sql_for_spark(self, mocker) -> None:
        given_dataset = build_dataset()
        given_dataframe = mocker.Mock()
        mock_run_sql_files = mocker.patch.object(system_under_test, "run_sql_files")
        mock_populate_stage = mocker.patch.object(system_under_test, "populate_stage_from_spark")

        system_under_test.truncate_and_populate_from_spark(given_dataset, given_dataframe)

        assert mock_run_sql_files.call_count == 2
        assert mock_populate_stage.call_count == 1
