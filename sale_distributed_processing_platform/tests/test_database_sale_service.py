import pandas as pd
import pytest
from pandas import DataFrame as PandasDataFrame
from pyspark.sql import DataFrame as SparkDataFrame

from service import database_sale_service as system_under_test


class TestPopulationStrategyRegistration:

    def test_should_register_pandas_population_strategy(self) -> None:
        # Given
        given_dataframe_type = PandasDataFrame

        # When
        actual = system_under_test.PopulationStrategy._registry[given_dataframe_type]

        # Then
        assert actual is system_under_test.PandasPopulationStrategy

    def test_should_register_spark_population_strategy(self) -> None:
        # Given
        given_dataframe_type = SparkDataFrame

        # When
        actual = system_under_test.PopulationStrategy._registry[given_dataframe_type]

        # Then
        assert actual is system_under_test.SparkPopulationStrategy

    def test_should_register_strategy_automatically(self, monkeypatch) -> None:
        # Given
        class GivenDataFrame:
            pass

        given_registry = {}
        monkeypatch.setattr(system_under_test.PopulationStrategy, "_registry", given_registry)

        # When
        class GivenPopulationStrategy(
            system_under_test.PopulationStrategy[GivenDataFrame],
            dataframe_type=GivenDataFrame
        ):
            def populate_sale_stage(self) -> None:
                pass

        actual = system_under_test.PopulationStrategy._registry

        # Then
        assert actual[GivenDataFrame] is GivenPopulationStrategy
        assert GivenPopulationStrategy.dataframe_type is GivenDataFrame

    def test_should_not_register_strategy_without_dataframe_type(self, monkeypatch) -> None:
        # Given
        given_registry = {}
        monkeypatch.setattr(system_under_test.PopulationStrategy, "_registry", given_registry)

        # When
        class GivenPopulationStrategy(system_under_test.PopulationStrategy[PandasDataFrame]):
            def populate_sale_stage(self) -> None:
                pass

        actual = system_under_test.PopulationStrategy._registry

        # Then
        assert actual == {}
        assert GivenPopulationStrategy.dataframe_type is None

    def test_should_raise_error_when_dataframe_type_is_already_registered(self, monkeypatch) -> None:
        # Given
        class GivenDataFrame:
            pass

        class GivenRegisteredStrategy(system_under_test.PopulationStrategy[GivenDataFrame]):
            def populate_sale_stage(self) -> None:
                pass

        given_registry = {GivenDataFrame: GivenRegisteredStrategy, }
        given_error_message = ("A strategy is already registered for GivenDataFrame: GivenRegisteredStrategy")

        monkeypatch.setattr(system_under_test.PopulationStrategy, "_registry", given_registry, )

        # When
        with pytest.raises(ValueError) as actual:
            class GivenDuplicateStrategy(
                system_under_test.PopulationStrategy[GivenDataFrame],
                dataframe_type=GivenDataFrame
            ):
                def populate_sale_stage(self) -> None:
                    pass

        # Then
        assert str(actual.value) == given_error_message


class TestFindPopulationStrategyType:

    def test_should_find_strategy_by_exact_dataframe_type(self, monkeypatch) -> None:
        # Given
        given_dataframe = pd.DataFrame()
        given_registry = {PandasDataFrame: system_under_test.PandasPopulationStrategy, }

        monkeypatch.setattr(system_under_test.PopulationStrategy, "_registry", given_registry, )

        # When
        actual = system_under_test.PopulationStrategy._find_strategy_type(given_dataframe)

        # Then
        assert actual is system_under_test.PandasPopulationStrategy

    def test_should_find_strategy_by_parent_dataframe_type(self, monkeypatch) -> None:
        # Given
        class GivenParentDataFrame:
            pass

        class GivenChildDataFrame(GivenParentDataFrame):
            pass

        class GivenPopulationStrategy(system_under_test.PopulationStrategy[GivenParentDataFrame]):
            def populate_sale_stage(self) -> None:
                pass

        given_dataframe = GivenChildDataFrame()
        given_registry = {GivenParentDataFrame: GivenPopulationStrategy}

        monkeypatch.setattr(system_under_test.PopulationStrategy, "_registry", given_registry)

        # When
        actual = system_under_test.PopulationStrategy._find_strategy_type(given_dataframe)

        # Then
        assert actual is GivenPopulationStrategy

    def test_should_return_none_when_strategy_is_not_registered(self, monkeypatch) -> None:
        # Given
        class GivenUnsupportedDataFrame:
            pass

        given_dataframe = GivenUnsupportedDataFrame()
        given_registry = {}

        monkeypatch.setattr(system_under_test.PopulationStrategy, "_registry", given_registry)

        # When
        actual = system_under_test.PopulationStrategy._find_strategy_type(given_dataframe)

        # Then
        assert actual is None


class TestCreatePopulationStrategy:

    def test_should_create_pandas_population_strategy(self, monkeypatch) -> None:
        # Given
        given_dataframe = pd.DataFrame()
        given_registry = {PandasDataFrame: system_under_test.PandasPopulationStrategy}

        monkeypatch.setattr(system_under_test.PopulationStrategy, "_registry", given_registry)

        # When
        actual = system_under_test.PopulationStrategy.create(given_dataframe)

        # Then
        assert isinstance(actual, system_under_test.PandasPopulationStrategy)
        assert actual._dataframe is given_dataframe

    def test_should_raise_error_when_strategy_is_not_registered(self, monkeypatch) -> None:
        # Given
        class GivenUnsupportedDataFrame:
            pass

        given_dataframe = GivenUnsupportedDataFrame()
        given_registry = {PandasDataFrame: system_under_test.PandasPopulationStrategy}
        given_error_message = (
            "No sale-stage population strategy is registered for GivenUnsupportedDataFrame. Registered DataFrame types: DataFrame"
        )

        monkeypatch.setattr(system_under_test.PopulationStrategy, "_registry", given_registry)

        # When
        with pytest.raises(TypeError) as actual:
            system_under_test.PopulationStrategy.create(given_dataframe)

        # Then
        assert str(actual.value) == given_error_message

    def test_should_show_none_when_registry_is_empty(self, monkeypatch) -> None:
        # Given
        class GivenUnsupportedDataFrame:
            pass

        given_dataframe = GivenUnsupportedDataFrame()
        given_registry = {}
        given_error_message = (
            "No sale-stage population strategy is registered for GivenUnsupportedDataFrame. Registered DataFrame types: none"
        )

        monkeypatch.setattr(system_under_test.PopulationStrategy, "_registry", given_registry)

        # When
        with pytest.raises(TypeError) as actual:
            system_under_test.PopulationStrategy.create(given_dataframe)

        # Then
        assert str(actual.value) == given_error_message


class TestPandasPopulationStrategy:

    def test_should_populate_sale_stage_table(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock()
        given_database_engine = mocker.Mock()
        given_database_connection = mocker.Mock()
        given_transaction_context = mocker.MagicMock()

        given_transaction_context.__enter__.return_value = given_database_connection
        given_database_engine.begin.return_value = given_transaction_context

        mock_create_connection = mocker.patch.object(
            system_under_test.database_connection_factory,
            "create_connection",
            return_value=given_database_engine
        )

        given_strategy = system_under_test.PandasPopulationStrategy(given_dataframe)

        # When
        given_strategy.populate_sale_stage()

        # Then
        mock_create_connection.assert_called_once_with()
        given_database_engine.begin.assert_called_once_with()
        given_transaction_context.__enter__.assert_called_once_with()
        given_transaction_context.__exit__.assert_called_once()

        given_dataframe.to_sql.assert_called_once_with(
            name=system_under_test.ec.DATABASE_SALE_STAGE_TABLE,
            con=given_database_connection,
            if_exists="append",
            index=False,
        )


class TestSparkPopulationStrategy:

    def test_should_populate_sale_stage_table(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock()
        given_writer = given_dataframe.write

        given_writer.format.return_value = given_writer
        given_writer.option.return_value = given_writer
        given_writer.mode.return_value = given_writer

        given_strategy = system_under_test.SparkPopulationStrategy(given_dataframe)

        # When
        given_strategy.populate_sale_stage()

        # Then
        assert given_writer.format.call_count == 1
        assert given_writer.option.call_count == 5
        assert given_writer.mode.call_count == 1
        assert given_writer.save.call_count == 1

        given_writer.format.assert_called_with("jdbc")
        given_writer.mode.assert_called_with("append")

        given_writer.option.assert_any_call("url", system_under_test.ec.DATABASE_JDBC_URL)
        given_writer.option.assert_any_call("dbtable", system_under_test.ec.DATABASE_SALE_STAGE_TABLE)
        given_writer.option.assert_any_call("user", system_under_test.ec.DATABASE_USER)
        given_writer.option.assert_any_call("password", system_under_test.ec.DATABASE_PASSWORD)
        given_writer.option.assert_any_call("driver", system_under_test.ec.DATABASE_DRIVER)


class TestSaleDatabasePopulationService:

    def test_should_truncate_sale_stage(self, mocker) -> None:
        # Given
        mock_execute_sql = mocker.patch.object(system_under_test, "execute_sql")

        # When
        system_under_test.SaleDatabasePopulationService._truncate_sale_stage()

        # Then
        assert mock_execute_sql.call_count == 1

        mock_execute_sql.assert_called_with(
            system_under_test.DatabaseQueries.TRUNCATE_SALE_STAGE
        )

    def test_should_populate_normalized_sale_tables(self, mocker) -> None:
        # Given
        mock_execute_sql = mocker.patch.object(system_under_test, "execute_sql")

        # When
        system_under_test.SaleDatabasePopulationService._populate_normalized_sale_tables()

        # Then
        assert mock_execute_sql.call_count == 1

        mock_execute_sql.assert_called_with(
            system_under_test.DatabaseQueries.TRUNCATE_NORMALIZED_TABLES,
            system_under_test.DatabaseQueries.INSERT_CUSTOMERS,
            system_under_test.DatabaseQueries.INSERT_PRODUCTS,
            system_under_test.DatabaseQueries.INSERT_ORDERS,
            system_under_test.DatabaseQueries.INSERT_ORDER_ITEMS,
        )

    def test_should_execute_all_population_steps(self, mocker) -> None:
        # Given
        given_population_strategy = mocker.Mock()

        given_service = system_under_test.SaleDatabasePopulationService(given_population_strategy)

        mock_truncate_sale_stage = mocker.patch.object(given_service, "_truncate_sale_stage", )
        mock_populate_normalized_sale_tables = mocker.patch.object(given_service, "_populate_normalized_sale_tables", )

        # When
        given_service.populate()

        # Then
        assert mock_truncate_sale_stage.call_count == 1
        assert given_population_strategy.populate_sale_stage.call_count == 1
        assert mock_populate_normalized_sale_tables.call_count == 1

    def test_should_not_populate_normalized_tables_when_stage_population_fails(self, mocker) -> None:
        # Given
        given_error_message = "Stage population failed"
        given_population_strategy = mocker.Mock()
        given_population_strategy.populate_sale_stage.side_effect = (RuntimeError(given_error_message))

        given_service = system_under_test.SaleDatabasePopulationService(given_population_strategy)

        mocker.patch.object(given_service, "_truncate_sale_stage")
        mock_populate_normalized_sale_tables = mocker.patch.object(given_service, "_populate_normalized_sale_tables")

        # When
        with pytest.raises(RuntimeError) as actual:
            given_service.populate()

        # Then
        assert str(actual.value) == given_error_message
        assert mock_populate_normalized_sale_tables.call_count == 0


class TestPopulateSaleData:

    def test_should_create_strategy_and_populate_sale_data(self, mocker) -> None:
        # Given
        given_dataframe = pd.DataFrame()
        given_population_strategy = mocker.Mock()
        given_population_service = mocker.Mock()

        mock_create_strategy = mocker.patch.object(
            system_under_test.PopulationStrategy,
            "create",
            return_value=given_population_strategy,
        )

        mock_population_service = mocker.patch.object(
            system_under_test,
            "SaleDatabasePopulationService",
            return_value=given_population_service,
        )

        # When
        system_under_test.populate_sale_data(given_dataframe)

        # Then
        assert mock_create_strategy.call_count == 1
        assert mock_population_service.call_count == 1
        assert given_population_service.populate.call_count == 1

        mock_create_strategy.assert_called_with(given_dataframe)
        mock_population_service.assert_called_with(given_population_strategy)
