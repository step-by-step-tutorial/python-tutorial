from data_platform.analyzers.aggregate_model import AggregateSpecification
from data_platform.analyzers.spark_analyzer_chain import SparkAnalyzerChain
from data_platform.analyzers.spark_analyzer_impl import GroupAggregateAnalyzer
from data_platform.cleaners.spark_cleaner_chain import SparkCleanerChain
from data_platform.cleaners.spark_cleaner_impl import DropDuplicatesCleaner, NumericColumnCleaner, StripColumnCleaner, \
    ToDatetimeCleaner
from data_platform.config.keys import Key
from data_platform.connector.spark_session_factory import create_session
from data_platform.domain.online_shopping.attribute import attribute
from data_platform.domain.online_shopping.spark_schema import ONLINE_SHOPPING_SCHEMA
from data_platform.enrichers.spark_enricher_chain import SparkEnricherChain
from data_platform.enrichers.spark_enricher_impl import CopyColumnEnricher, DatetimePartEnricher, PercentageEnricher
from data_platform.ingestion.spark_rest_api_csv_ingestor import SparkRestApiCsvIngestor
from data_platform.model.dataframe_model import DataFrameModel
from data_platform.model.dataset import Dataset
from data_platform.model.spark_pipeline_flow import SparkPipelineFlow
from data_platform.registry.endpoint_registry import endpoint_registry
from data_platform.repository.data_exposer import DataExposer
from data_platform.repository.spark_database_repository import SparkDatabaseRepository
from data_platform.repository.spark_datalake_repository import SparkDatalakeRepository
from data_platform.repository.spark_warehouse_repository import SparkWarehouseRepository
from data_platform.validators.spark_validator_chain import SparkValidatorChain
from data_platform.validators.spark_validator_impl import NonNegativeValidator, NotNullValidator, PositiveValidator, \
    RequiredColumnsValidator

online_shopping_spark_endpoints = {
    Key.ONLINE_SHOPPING_REST_API: endpoint_registry.get_item(Key.ONLINE_SHOPPING_REST_API),
    Key.ONLINE_SHOPPING_DATA_LAKE: endpoint_registry.get_item(Key.ONLINE_SHOPPING_DATA_LAKE),
    Key.ONLINE_SHOPPING_BACKUP_DATA_LAKE: endpoint_registry.get_item(Key.ONLINE_SHOPPING_BACKUP_DATA_LAKE),
    Key.ONLINE_SHOPPING_DATABASE: endpoint_registry.get_item(Key.ONLINE_SHOPPING_DATABASE),
    Key.ONLINE_SHOPPING_WAREHOUSE: endpoint_registry.get_item(Key.ONLINE_SHOPPING_WAREHOUSE),
}

spark_online_shopping_dataset = Dataset(
    name="online_shopping",
    audit=endpoint_registry.get_item("audit"),
    dataframe=DataFrameModel(
        schema=ONLINE_SHOPPING_SCHEMA,
        required_columns=frozenset(
            {attribute.order_id, attribute.order_date, attribute.sales_channel, attribute.country,
             attribute.product_name, attribute.unit_price, attribute.quantity, attribute.total_amount}),
    ),
    endpoints=online_shopping_spark_endpoints,
    flow=SparkPipelineFlow(
        repository=SparkDatalakeRepository(create_session,
                                           online_shopping_spark_endpoints[Key.ONLINE_SHOPPING_DATA_LAKE]),
        backup_repository=SparkDatalakeRepository(create_session, online_shopping_spark_endpoints[
            Key.ONLINE_SHOPPING_BACKUP_DATA_LAKE]),
        ingestors=(
            SparkRestApiCsvIngestor(online_shopping_spark_endpoints[Key.ONLINE_SHOPPING_REST_API], create_session,
                                    ONLINE_SHOPPING_SCHEMA),),
        cleaners=SparkCleanerChain((DropDuplicatesCleaner(attribute.order_id), ToDatetimeCleaner(attribute.order_date),
                                    ToDatetimeCleaner(attribute.estimated_delivery_date),
                                    StripColumnCleaner(attribute.phone), *(NumericColumnCleaner(column) for column in
                                                                           (attribute.customer_id, attribute.unit_price,
                                                                            attribute.quantity, attribute.subtotal,
                                                                            attribute.discount_percent,
                                                                            attribute.shipping_cost,
                                                                            attribute.tax_amount,
                                                                            attribute.total_amount,
                                                                            attribute.delivery_days)))),
        validators=SparkValidatorChain((RequiredColumnsValidator(
            (attribute.order_id, attribute.order_date, attribute.quantity, attribute.unit_price,
             attribute.total_amount)), NotNullValidator(attribute.order_id), NotNullValidator(attribute.order_date),
                                        PositiveValidator(attribute.quantity),
                                        NonNegativeValidator(attribute.unit_price),
                                        NonNegativeValidator(attribute.total_amount))),
        enrichers=SparkEnricherChain(
            (PercentageEnricher(attribute.subtotal, attribute.discount_percent, attribute.discount_amount),
             CopyColumnEnricher(attribute.total_amount, attribute.net_revenue, decimals=2),
             DatetimePartEnricher(attribute.order_date, "year", attribute.year),
             DatetimePartEnricher(attribute.order_date, "month", attribute.month))),
        exposers=(DataExposer(
            (SparkDatabaseRepository(online_shopping_spark_endpoints[Key.ONLINE_SHOPPING_DATABASE]).overwrite,
             SparkWarehouseRepository(online_shopping_spark_endpoints[Key.ONLINE_SHOPPING_WAREHOUSE]).overwrite)),),
        analyzers=SparkAnalyzerChain((
            GroupAggregateAnalyzer("revenue_by_country",
                                   AggregateSpecification(attribute.country, attribute.net_revenue, "sum",
                                                          attribute.revenue)),
            GroupAggregateAnalyzer("revenue_by_sales_channel",
                                   AggregateSpecification(attribute.sales_channel, attribute.net_revenue, "sum",
                                                          attribute.revenue)),
            GroupAggregateAnalyzer("order_count_by_country",
                                   AggregateSpecification(attribute.country, attribute.order_id, "count",
                                                          "order_count")),
            GroupAggregateAnalyzer("revenue_by_category",
                                   AggregateSpecification(attribute.category, attribute.net_revenue, "sum",
                                                          attribute.revenue)),
            GroupAggregateAnalyzer("average_order_value_by_sales_channel",
                                   AggregateSpecification(attribute.sales_channel, attribute.total_amount, "avg",
                                                          "average_order_value")),
            GroupAggregateAnalyzer("average_delivery_days_by_shipping_method",
                                   AggregateSpecification(attribute.shipping_method, attribute.delivery_days, "avg",
                                                          "average_delivery_days")),
            GroupAggregateAnalyzer("order_count_by_fulfillment_status",
                                   AggregateSpecification(attribute.fulfillment_status, attribute.order_id, "count",
                                                          "order_count")),
        )),
    ),
)
