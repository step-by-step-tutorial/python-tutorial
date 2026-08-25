from data_platform.analyzers.analyzer_chain import AnalyzerChain
from data_platform.analyzers.analyzer_impl import GroupAggregateAnalyzer
from data_platform.cleaners import (
    CastColumnCleaner,
    CleanerChain,
    DropDuplicatesCleaner,
    FillMissingByColumnAverageCleaner,
    FillMissingByGroupAverageCleaner,
    NumericColumnCleaner,
    ToDatetimeCleaner,
)
from data_platform.config.keys import Key
from data_platform.domain.sale.attribute import SALE_ATTRIBUTE
from data_platform.domain.sale.spark_schema import build_schema
from data_platform.enrichers import DatetimePartEnricher, EnricherChain, MultiplyColumnsEnricher
from data_platform.ingestion.csv_file_ingestor import CsvFileIngestor
from data_platform.model import (
    DataFrameModel,
    Dataset,
    PipelineFlow,
)
from data_platform.persistence.data_lake_repository import DataLakeRepository
from data_platform.persistence.inmemory_database_repository import (
    PandasDatabaseRepository,
)
from data_platform.persistence.inmemory_warehouse_repository import (
    PandasWarehouseRepository,
)
from data_platform.persistence.repository_data_exposer import RepositoryDataExposer
from data_platform.registry.endpoint_registry import endpoint_registry
from data_platform.validators import (
    NonNegativeValidator,
    NotNullValidator,
    PositiveValidator,
    RequiredColumnsValidator,
    ValidatorChain,
)

SALE_DATASET = Dataset(
    name="sale",
    dataframe=DataFrameModel(
        schema=build_schema(),
        required_columns=frozenset(
            {
                SALE_ATTRIBUTE.order_id,
                SALE_ATTRIBUTE.customer_name,
                SALE_ATTRIBUTE.product_name,
                SALE_ATTRIBUTE.category,
                SALE_ATTRIBUTE.quantity,
                SALE_ATTRIBUTE.unit_price,
                SALE_ATTRIBUTE.order_date,
                SALE_ATTRIBUTE.country,
            }
        ),
    ),
    audit=endpoint_registry.get_item("audit"),
    endpoints={
        Key.SALE_CSV_FILE: (
            endpoint_registry.get_item(Key.SALE_CSV_FILE)
        ),
        Key.SALE_REST_API: (
            endpoint_registry.get_item(Key.SALE_REST_API)
        ),
        Key.SALE_KAFKA_CONSUMER: (
            endpoint_registry.get_item(Key.SALE_KAFKA_CONSUMER)
        ),
        Key.SALE_KAFKA_PRODUCER: (
            endpoint_registry.get_item(Key.SALE_KAFKA_PRODUCER)
        ),
        Key.SALE_DATA_LAKE: (
            endpoint_registry.get_item(Key.SALE_DATA_LAKE)
        ),
        Key.SALE_DATABASE: (
            endpoint_registry.get_item(Key.SALE_DATABASE)
        ),
        Key.SALE_WAREHOUSE: (
            endpoint_registry.get_item(Key.SALE_WAREHOUSE)
        ),
    },
    flow=PipelineFlow(
        repository=DataLakeRepository(
            endpoint_registry.get_item(Key.SALE_DATA_LAKE)
        ),
        ingestors=(
            CsvFileIngestor(
                endpoint_registry.get_item(Key.SALE_CSV_FILE)
            ),
        ),
        cleaners=CleanerChain((
            DropDuplicatesCleaner(SALE_ATTRIBUTE.order_id),
            NumericColumnCleaner(SALE_ATTRIBUTE.quantity, default_value=1.0),
            NumericColumnCleaner(SALE_ATTRIBUTE.unit_price),
            FillMissingByGroupAverageCleaner(SALE_ATTRIBUTE.category, SALE_ATTRIBUTE.unit_price),
            FillMissingByColumnAverageCleaner(SALE_ATTRIBUTE.unit_price),
            ToDatetimeCleaner(SALE_ATTRIBUTE.order_date),
            CastColumnCleaner(SALE_ATTRIBUTE.order_id, "int64"),
            CastColumnCleaner(SALE_ATTRIBUTE.quantity, "float64"),
            CastColumnCleaner(SALE_ATTRIBUTE.unit_price, "float64"),
        )),
        validators=ValidatorChain((
            RequiredColumnsValidator((
                SALE_ATTRIBUTE.order_id, SALE_ATTRIBUTE.quantity,
                SALE_ATTRIBUTE.unit_price, SALE_ATTRIBUTE.order_date,
            )),
            NotNullValidator(SALE_ATTRIBUTE.order_date),
            PositiveValidator(SALE_ATTRIBUTE.quantity),
            NonNegativeValidator(SALE_ATTRIBUTE.unit_price),
        )),
        enrichers=EnricherChain((
            MultiplyColumnsEnricher(SALE_ATTRIBUTE.quantity, SALE_ATTRIBUTE.unit_price, SALE_ATTRIBUTE.total_price),
            DatetimePartEnricher(SALE_ATTRIBUTE.order_date, "year", SALE_ATTRIBUTE.year),
            DatetimePartEnricher(SALE_ATTRIBUTE.order_date, "month", SALE_ATTRIBUTE.month),
        )),
        exposers=(
            RepositoryDataExposer((
                PandasDatabaseRepository(
                    (
                        endpoint_registry.get_item(Key.SALE_DATABASE)
                    )
                ).replace,
            )),
            RepositoryDataExposer((
                PandasWarehouseRepository(
                    (
                        endpoint_registry.get_item(Key.SALE_WAREHOUSE)
                    )
                ).replace,
            )),
        ),
        analyzers=AnalyzerChain((
            GroupAggregateAnalyzer("revenue_by_category", SALE_ATTRIBUTE.category, SALE_ATTRIBUTE.total_price, "sum",
                                   SALE_ATTRIBUTE.revenue),
            GroupAggregateAnalyzer("revenue_by_country", SALE_ATTRIBUTE.country, SALE_ATTRIBUTE.total_price, "sum",
                                   SALE_ATTRIBUTE.revenue),
        )),
    ),
)
