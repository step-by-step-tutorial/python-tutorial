import pandas
import pytest
import pyspark.sql

from service.database import database_population_strategy as system_under_test


class TestPopulationFunctions:

    def test_should_contain_pandas_population_function(self) -> None:
        # When
        actual = system_under_test.POPULATION_FUNCTIONS[pandas.DataFrame]

        # Then
        assert actual is system_under_test.populate_stage_from_pandas

    def test_should_contain_spark_population_function(self) -> None:
        # When
        actual = system_under_test.POPULATION_FUNCTIONS[pyspark.sql.DataFrame]

        # Then
        assert actual is system_under_test.populate_stage_from_spark


class TestPopulateStageFromPandas:

    def test_should_populate_stage_table(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock(spec=pandas.DataFrame)
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

        # When
        actual = system_under_test.populate_stage_from_pandas(given_dataframe, "sale.example_stage")

        # Then
        assert actual is None
        assert mock_create_connection.call_count == 1
        assert given_database_engine.begin.call_count == 1
        assert given_transaction_context.__enter__.call_count == 1
        assert given_transaction_context.__exit__.call_count == 1
        assert given_dataframe.to_sql.call_count == 1

    def test_should_propagate_error_when_population_fails(self, mocker) -> None:
        # Given
        given_error_message = "Pandas stage population failed"
        given_dataframe = mocker.Mock(spec=pandas.DataFrame)
        given_database_engine = mocker.Mock()
        given_transaction_context = mocker.MagicMock()

        given_database_engine.begin.return_value = given_transaction_context
        given_dataframe.to_sql.side_effect = RuntimeError(given_error_message)

        mocker.patch.object(
            system_under_test.database_connection_factory,
            "create_connection",
            return_value=given_database_engine,
        )

        # When
        with pytest.raises(RuntimeError) as actual:
            system_under_test.populate_stage_from_pandas(given_dataframe, "sale.example_stage")

        # Then
        assert str(actual.value) == given_error_message


class TestPopulateStageFromSpark:

    def test_should_populate_stage_table(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock(spec=pyspark.sql.DataFrame)
        given_writer = mocker.Mock()

        given_dataframe.write = given_writer
        given_writer.format.return_value = given_writer
        given_writer.option.return_value = given_writer
        given_writer.mode.return_value = given_writer

        # When
        actual = system_under_test.populate_stage_from_spark(
            given_dataframe,
            "sale.example_stage",
            "jdbc:example",
            "user",
            "password",
            "driver",
        )

        # Then
        assert actual is None
        assert given_writer.format.call_count == 1
        assert given_writer.option.call_count == 5
        assert given_writer.mode.call_count == 1
        assert given_writer.save.call_count == 1

    def test_should_propagate_error_when_population_fails(self, mocker) -> None:
        # Given
        given_error_message = "Spark stage population failed"
        given_dataframe = mocker.Mock(spec=pyspark.sql.DataFrame)
        given_writer = mocker.Mock()

        given_dataframe.write = given_writer
        given_writer.format.return_value = given_writer
        given_writer.option.return_value = given_writer
        given_writer.mode.return_value = given_writer
        given_writer.save.side_effect = RuntimeError(given_error_message)

        # When
        with pytest.raises(RuntimeError) as actual:
            system_under_test.populate_stage_from_spark(
                given_dataframe,
                "sale.example_stage",
                "jdbc:example",
                "user",
                "password",
                "driver",
            )

        # Then
        assert str(actual.value) == given_error_message
