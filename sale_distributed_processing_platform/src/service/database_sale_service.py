from abc import ABC, abstractmethod
from typing import Any, ClassVar, Generic, TypeVar

from pandas import DataFrame as PandasDataFrame
from pyspark.sql import DataFrame as SparkDataFrame

from app_config import env_config as ec
from factory import database_connection_factory
from util.database_util import execute_sql
from util.text_file_utils import load_sql_query

DataFrameType = TypeVar(
    "DataFrameType",
    PandasDataFrame,
    SparkDataFrame,
)


class DatabaseQueries:
    TRUNCATE_SALE_STAGE = load_sql_query("truncate_sale_stage.sql")
    TRUNCATE_NORMALIZED_TABLES = load_sql_query("truncate_normalized_tables.sql")
    INSERT_CUSTOMERS = load_sql_query("insert_customers.sql")
    INSERT_PRODUCTS = load_sql_query("insert_products.sql")
    INSERT_ORDERS = load_sql_query("insert_orders.sql")
    INSERT_ORDER_ITEMS = load_sql_query("insert_order_items.sql")


class PopulationStrategy(ABC, Generic[DataFrameType]):
    _registry: ClassVar[dict[type[Any], type["PopulationStrategy[Any]"]]] = {}

    dataframe_type: ClassVar[type[Any] | None] = None

    def __init_subclass__(cls, *, dataframe_type: type[Any] | None = None, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        if dataframe_type is None:
            return

        if dataframe_type in cls._registry:
            registered_strategy = cls._registry[dataframe_type]

            raise ValueError(
                f"A strategy is already registered for {dataframe_type.__name__}: {registered_strategy.__name__}"
            )

        cls.dataframe_type = dataframe_type
        cls._registry[dataframe_type] = cls

    def __init__(self, dataframe: DataFrameType) -> None:
        self._dataframe = dataframe

    @abstractmethod
    def populate_sale_stage(self) -> None:
        pass

    @classmethod
    def create(cls, dataframe: PandasDataFrame | SparkDataFrame) -> "PopulationStrategy[Any]":
        strategy_type = cls._find_strategy_type(dataframe)
        if strategy_type is None:
            registered_types = ", ".join(registered_type.__name__ for registered_type in cls._registry)

            raise TypeError(
                f"No sale-stage population strategy is registered for {type(dataframe).__name__}. "
                f"Registered DataFrame types: {registered_types or 'none'}"
            )

        return strategy_type(dataframe)

    @classmethod
    def _find_strategy_type(cls, dataframe: PandasDataFrame | SparkDataFrame) -> type["PopulationStrategy[Any]"] | None:
        dataframe_type = type(dataframe)
        exact_strategy_type = cls._registry.get(dataframe_type)

        if exact_strategy_type is not None:
            return exact_strategy_type

        for registered_type, strategy_type in cls._registry.items():
            if isinstance(dataframe, registered_type):
                return strategy_type

        return None


class SparkPopulationStrategy(PopulationStrategy[SparkDataFrame], dataframe_type=SparkDataFrame):
    def populate_sale_stage(self) -> None:
        (
            self._dataframe.write
            .format("jdbc")
            .option("url", ec.DATABASE_JDBC_URL)
            .option("dbtable", ec.DATABASE_SALE_STAGE_TABLE)
            .option("user", ec.DATABASE_USER)
            .option("password", ec.DATABASE_PASSWORD)
            .option("driver", ec.DATABASE_DRIVER)
            .mode("append")
            .save()
        )


class PandasPopulationStrategy(PopulationStrategy[PandasDataFrame], dataframe_type=PandasDataFrame):
    def populate_sale_stage(self) -> None:
        with database_connection_factory.create_connection().begin() as connection:
            self._dataframe.to_sql(name=ec.DATABASE_SALE_STAGE_TABLE, con=connection, if_exists="append", index=False)


class SaleDatabasePopulationService:
    def __init__(self, population_strategy: (PopulationStrategy[Any])) -> None:
        self._population_strategy = population_strategy

    def populate(self) -> None:
        self._truncate_sale_stage()
        self._population_strategy.populate_sale_stage()
        self._populate_normalized_sale_tables()

    @staticmethod
    def _truncate_sale_stage() -> None:
        execute_sql(DatabaseQueries.TRUNCATE_SALE_STAGE)

    @staticmethod
    def _populate_normalized_sale_tables() -> None:
        execute_sql(
            DatabaseQueries.TRUNCATE_NORMALIZED_TABLES,
            DatabaseQueries.INSERT_CUSTOMERS,
            DatabaseQueries.INSERT_PRODUCTS,
            DatabaseQueries.INSERT_ORDERS,
            DatabaseQueries.INSERT_ORDER_ITEMS,
        )


def populate_sale_data(dataframe: PandasDataFrame | SparkDataFrame) -> None:
    SaleDatabasePopulationService(PopulationStrategy.create(dataframe)).populate()
