from data_platform.analyzers.analyzer_chain import AnalyzerChain
from data_platform.analyzers.analyzer_impl import GroupAggregateAnalyzer
from data_platform.analyzers.aggregate_model import AggregateSpecification
from data_platform.cleaners.cleaner_impl import (
    CleanerChain,
    DropDuplicatesCleaner,
    NumericColumnCleaner,
    StripColumnCleaner,
    ToDatetimeCleaner,
)
from data_platform.config.keys import Key
from data_platform.domain.online_shopping.attribute import attribute
from data_platform.domain.online_shopping.spark_schema import ONLINE_SHOPPING_SCHEMA
from data_platform.enrichers.enricher_impl import CopyColumnEnricher, DatetimePartEnricher, EnricherChain, PercentageEnricher
from data_platform.ingestion.rest_api_csv_ingestor import RestApiCsvIngestor
from data_platform.model.dataframe_model import DataFrameModel
from data_platform.model.dataset import Dataset
from data_platform.model.pipeline_flow import PipelineFlow

from data_platform.repository.inmemory_datalake_repository import DataLakeRepository
from data_platform.repository.inmemory_database_repository import InmemoryDatabaseRepository
from data_platform.repository.inmemory_warehouse_repository import InmemoryWarehouseRepository
from data_platform.repository.data_exposer import DataExposer
from data_platform.registry.endpoint_registry import endpoint_registry
from data_platform.validators.validator_impl import NonNegativeValidator, NotNullValidator, PositiveValidator, \
    RequiredColumnsValidator
from data_platform.validators.validator_chain import ValidatorChain

ONLINE_SHOPPING_DATASET = Dataset(
    name="online_shopping",
    dataframe=DataFrameModel(
        schema=ONLINE_SHOPPING_SCHEMA,
        required_columns=frozenset(
            {
                attribute.order_id,
                attribute.order_date,
                attribute.sales_channel,
                attribute.country,
                attribute.product_name,
                attribute.unit_price,
                attribute.quantity,
                attribute.total_amount,
            }
        )
    ),
    audit=endpoint_registry.get_item("audit"),
    endpoints={
        Key.ONLINE_SHOPPING_REST_API: endpoint_registry.get_item(Key.ONLINE_SHOPPING_REST_API),
        Key.ONLINE_SHOPPING_DATA_LAKE: endpoint_registry.get_item(Key.ONLINE_SHOPPING_DATA_LAKE),
        Key.ONLINE_SHOPPING_BACKUP_DATA_LAKE: endpoint_registry.get_item(Key.ONLINE_SHOPPING_BACKUP_DATA_LAKE),
        Key.ONLINE_SHOPPING_DATABASE: endpoint_registry.get_item(Key.ONLINE_SHOPPING_DATABASE),
        Key.ONLINE_SHOPPING_WAREHOUSE: endpoint_registry.get_item(Key.ONLINE_SHOPPING_WAREHOUSE),
    },
    flow=PipelineFlow(
        repository=DataLakeRepository(endpoint_registry.get_item(Key.ONLINE_SHOPPING_DATA_LAKE)),
        backup_repository=DataLakeRepository(endpoint_registry.get_item(Key.ONLINE_SHOPPING_BACKUP_DATA_LAKE)),
        ingestors=(
            RestApiCsvIngestor(endpoint_registry.get_item(Key.ONLINE_SHOPPING_REST_API)),
        ),
        cleaners=CleanerChain((
            DropDuplicatesCleaner(attribute.order_id),
            ToDatetimeCleaner(attribute.order_date),
            ToDatetimeCleaner(attribute.estimated_delivery_date),
            StripColumnCleaner(attribute.phone),
            NumericColumnCleaner(attribute.customer_id),
            NumericColumnCleaner(attribute.unit_price),
            NumericColumnCleaner(attribute.quantity),
            NumericColumnCleaner(attribute.subtotal),
            NumericColumnCleaner(attribute.discount_percent),
            NumericColumnCleaner(attribute.shipping_cost),
            NumericColumnCleaner(attribute.tax_amount),
            NumericColumnCleaner(attribute.total_amount),
            NumericColumnCleaner(attribute.delivery_days),
        )),
        validators=ValidatorChain((
            RequiredColumnsValidator(
                (
                    attribute.order_id,
                    attribute.order_date,
                    attribute.quantity,
                    attribute.unit_price,
                    attribute.total_amount
                )
            ),
            NotNullValidator(attribute.order_id),
            NotNullValidator(attribute.order_date),
            PositiveValidator(attribute.quantity),
            NonNegativeValidator(attribute.unit_price),
            NonNegativeValidator(attribute.total_amount),
        )),
        enrichers=EnricherChain((
            PercentageEnricher(attribute.subtotal, attribute.discount_percent, attribute.discount_amount),
            CopyColumnEnricher(attribute.total_amount, attribute.net_revenue, decimals=2),
            DatetimePartEnricher(attribute.order_date, "year", attribute.year),
            DatetimePartEnricher(attribute.order_date, "month", attribute.month),
        )),
        exposers=(
            DataExposer((
                InmemoryDatabaseRepository(endpoint_registry.get_item(Key.ONLINE_SHOPPING_DATABASE)).overwrite,
                InmemoryWarehouseRepository(endpoint_registry.get_item(Key.ONLINE_SHOPPING_WAREHOUSE)).overwrite,
            )),
        ),
        analyzers=AnalyzerChain((
            GroupAggregateAnalyzer("revenue_by_country", AggregateSpecification(
                attribute.country,
                attribute.net_revenue,
                "sum",
                attribute.revenue
            )),
            GroupAggregateAnalyzer("revenue_by_sales_channel", AggregateSpecification(
                attribute.sales_channel,
                attribute.net_revenue,
                "sum",
                attribute.revenue
            )),
            GroupAggregateAnalyzer("order_count_by_country", AggregateSpecification(
                attribute.country,
                attribute.order_id,
                "count",
                "order_count"
            )),
            GroupAggregateAnalyzer("revenue_by_category", AggregateSpecification(
                attribute.category,
                attribute.net_revenue,
                "sum",
                attribute.revenue
            )),
            GroupAggregateAnalyzer("average_order_value_by_sales_channel", AggregateSpecification(
                attribute.sales_channel,
                attribute.total_amount,
                "mean",
                "average_order_value"
            )),
            GroupAggregateAnalyzer("average_delivery_days_by_shipping_method", AggregateSpecification(
                attribute.shipping_method,
                attribute.delivery_days,
                "mean",
                "average_delivery_days"
            )),
            GroupAggregateAnalyzer("order_count_by_fulfillment_status", AggregateSpecification(
                attribute.fulfillment_status,
                attribute.order_id,
                "count",
                "order_count"
            )),
        )),
    ),
)
