from data_platform.analyzers.analyzer_chain import AnalyzerChain
from data_platform.analyzers.analyzer_impl import GroupAggregateAnalyzer
from data_platform.analyzers.aggregate_model import AggregateSpecification
from data_platform.cleaners.cleaner_impl import CleanerChain, DropDuplicatesCleaner, NumericColumnCleaner, \
    FillMissingByGroupAverageCleaner, ToDatetimeCleaner, FillMissingByColumnAverageCleaner, CastColumnCleaner

from data_platform.config.keys import Key
from data_platform.domain.sale.attribute import attribute
from data_platform.domain.sale.spark_schema import build_schema
from data_platform.enrichers.enricher_impl import DatetimePartEnricher, EnricherChain, MultiplyColumnsEnricher
from data_platform.ingestion.csv_file_ingestor import CsvFileIngestor
from data_platform.model.dataframe_model import DataFrameModel
from data_platform.model.dataset import Dataset
from data_platform.model.pipeline_flow import PipelineFlow

from data_platform.repository.inmemory_datalake_repository import DataLakeRepository
from data_platform.repository.inmemory_database_repository import (
    InmemoryDataframeRepository,
)
from data_platform.repository.inmemory_warehouse_repository import (
    InmemoryWarehouseRepository,
)
from data_platform.repository.data_exposer import DataExposer
from data_platform.registry.endpoint_registry import endpoint_registry
from data_platform.validators.validator_impl import (
    NonNegativeValidator,
    NotNullValidator,
    PositiveValidator,
    RequiredColumnsValidator,
)
from data_platform.validators.validator_chain import ValidatorChain

sale_dataset = Dataset(
    name="sale",
    dataframe=DataFrameModel(
        schema=build_schema(),
        required_columns=frozenset(
            {
                attribute.order_id,
                attribute.customer_name,
                attribute.product_name,
                attribute.category,
                attribute.quantity,
                attribute.unit_price,
                attribute.order_date,
                attribute.country,
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
            DropDuplicatesCleaner(attribute.order_id),
            NumericColumnCleaner(attribute.quantity, default_value=1.0),
            NumericColumnCleaner(attribute.unit_price),
            FillMissingByGroupAverageCleaner(attribute.category, attribute.unit_price),
            FillMissingByColumnAverageCleaner(attribute.unit_price),
            ToDatetimeCleaner(attribute.order_date),
            CastColumnCleaner(attribute.order_id, "int64"),
            CastColumnCleaner(attribute.quantity, "float64"),
            CastColumnCleaner(attribute.unit_price, "float64"),
        )),
        validators=ValidatorChain((
            RequiredColumnsValidator((
                attribute.order_id, attribute.quantity,
                attribute.unit_price, attribute.order_date,
            )),
            NotNullValidator(attribute.order_date),
            PositiveValidator(attribute.quantity),
            NonNegativeValidator(attribute.unit_price),
        )),
        enrichers=EnricherChain((
            MultiplyColumnsEnricher(attribute.quantity, attribute.unit_price, attribute.total_price),
            DatetimePartEnricher(attribute.order_date, "year", attribute.year),
            DatetimePartEnricher(attribute.order_date, "month", attribute.month),
        )),
        exposers=(
            DataExposer((
                InmemoryDataframeRepository(
                    (
                        endpoint_registry.get_item(Key.SALE_DATABASE)
                    )
                ).overwrite,
            )),
            DataExposer((
                InmemoryWarehouseRepository(
                    (
                        endpoint_registry.get_item(Key.SALE_WAREHOUSE)
                    )
                ).overwrite,
            )),
        ),
        analyzers=AnalyzerChain((
            GroupAggregateAnalyzer("revenue_by_category", AggregateSpecification(attribute.category, attribute.total_price, "sum",
                                                                                 attribute.revenue)),
            GroupAggregateAnalyzer("revenue_by_country", AggregateSpecification(attribute.country, attribute.total_price, "sum",
                                                                                attribute.revenue)),
        )),
    ),
)
