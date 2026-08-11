import pandas
import pytest

from service.database import database_sale_service as system_under_test


class TestTruncateStageTable:

    def test_should_truncate_stage_table(self, mocker) -> None:
        # Given
        mock_execute_sql = mocker.patch.object(system_under_test, "execute_sql")

        # When
        system_under_test.truncate_stage_table()

        # Then
        assert mock_execute_sql.call_count == 1


class TestPopulateStageTable:

    def test_should_execute_population_function(self, mocker) -> None:
        # Given
        given_dataframe = pandas.DataFrame()
        given_population_function = mocker.Mock()
        mock_lookup_population_strategy = mocker.patch.object(
            system_under_test, "lookup_population_strategy",
            return_value=given_population_function
        )

        # When
        system_under_test.populate_stage_table(given_dataframe)

        # Then
        mock_lookup_population_strategy.assert_called_once_with(given_dataframe)
        given_population_function.assert_called_once_with(given_dataframe)

    def test_should_raise_error_for_unsupported_dataframe_type(self, mocker) -> None:
        # Given
        class GivenUnsupportedDataFrame:
            pass

        given_dataframe = GivenUnsupportedDataFrame()
        given_error_message = "Unsupported DataFrame type: GivenUnsupportedDataFrame"
        mocker.patch.object(system_under_test, "lookup_population_strategy", side_effect=TypeError(given_error_message))

        # When
        with pytest.raises(TypeError) as actual:
            system_under_test.populate_stage_table(given_dataframe)

        # Then
        assert str(actual.value) == given_error_message

    def test_should_not_execute_population_function_for_unsupported_type(self, mocker) -> None:
        # Given
        class GivenUnsupportedDataFrame:
            pass

        given_dataframe = GivenUnsupportedDataFrame()
        given_error_message = "Unsupported DataFrame type: GivenUnsupportedDataFrame"
        given_population_function = mocker.Mock()
        mocker.patch.object(system_under_test, "lookup_population_strategy", side_effect=TypeError(given_error_message))

        # When
        with pytest.raises(TypeError) as actual:
            system_under_test.populate_stage_table(given_dataframe)

        # Then
        assert str(actual.value) == given_error_message
        given_population_function.assert_not_called()


class TestTruncateAllTables:

    def test_should_truncate_all_tables(self, mocker) -> None:
        # Given
        mock_execute_sql = mocker.patch.object(system_under_test, "execute_sql")

        # When
        system_under_test.truncate_all_tables()

        # Then
        assert mock_execute_sql.call_count == 1


class TestPopulateAllTables:

    def test_should_populate_all_tables(self, mocker) -> None:
        # Given
        mock_execute_sql = mocker.patch.object(system_under_test, "execute_sql")

        # When
        system_under_test.populate_all_tables()

        # Then
        assert mock_execute_sql.call_count == 1


class TestPopulate:

    def test_should_execute_all_population_steps(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock()

        mock_truncate_stage_table = mocker.patch.object(system_under_test, "truncate_stage_table")
        mock_populate_stage_table = mocker.patch.object(system_under_test, "populate_stage_table")
        mock_truncate_all_tables = mocker.patch.object(system_under_test, "truncate_all_tables")
        mock_populate_all_tables = mocker.patch.object(system_under_test, "populate_all_tables")

        # When
        system_under_test.populate(given_dataframe)

        # Then
        assert mock_truncate_stage_table.call_count == 1
        assert mock_populate_stage_table.call_count == 1
        assert mock_truncate_all_tables.call_count == 1
        assert mock_populate_all_tables.call_count == 1

    def test_should_stop_when_stage_truncation_fails(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock()
        given_error_message = "Stage truncation failed"

        mocker.patch.object(system_under_test, "truncate_stage_table", side_effect=RuntimeError(given_error_message))
        mock_populate_stage_table = mocker.patch.object(system_under_test, "populate_stage_table")
        mock_truncate_all_tables = mocker.patch.object(system_under_test, "truncate_all_tables")
        mock_populate_all_tables = mocker.patch.object(system_under_test, "populate_all_tables")

        # When
        with pytest.raises(RuntimeError) as actual:
            system_under_test.populate(given_dataframe)

        # Then
        assert str(actual.value) == given_error_message
        assert mock_populate_stage_table.call_count == 0
        assert mock_truncate_all_tables.call_count == 0
        assert mock_populate_all_tables.call_count == 0

    def test_should_stop_when_stage_population_fails(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock()
        given_error_message = "Stage population failed"

        mock_truncate_stage_table = mocker.patch.object(system_under_test, "truncate_stage_table")
        mocker.patch.object(system_under_test, "populate_stage_table", side_effect=RuntimeError(given_error_message))
        mock_truncate_all_tables = mocker.patch.object(system_under_test, "truncate_all_tables")
        mock_populate_all_tables = mocker.patch.object(system_under_test, "populate_all_tables")

        # When
        with pytest.raises(RuntimeError) as actual:
            system_under_test.populate(given_dataframe)

        # Then
        assert str(actual.value) == given_error_message
        assert mock_truncate_stage_table.call_count == 1
        assert mock_truncate_all_tables.call_count == 0
        assert mock_populate_all_tables.call_count == 0

    def test_should_stop_when_all_table_truncation_fails(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock()
        given_error_message = "Table truncation failed"

        mock_truncate_stage_table = mocker.patch.object(system_under_test, "truncate_stage_table")
        mock_populate_stage_table = mocker.patch.object(system_under_test, "populate_stage_table")
        mocker.patch.object(system_under_test, "truncate_all_tables", side_effect=RuntimeError(given_error_message))
        mock_populate_all_tables = mocker.patch.object(system_under_test, "populate_all_tables")

        # When
        with pytest.raises(RuntimeError) as actual:
            system_under_test.populate(given_dataframe)

        # Then
        assert str(actual.value) == given_error_message
        assert mock_truncate_stage_table.call_count == 1
        assert mock_populate_stage_table.call_count == 1
        assert mock_populate_all_tables.call_count == 0
