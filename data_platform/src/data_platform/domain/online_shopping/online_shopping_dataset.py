from types import ModuleType

from data_platform.analyzer import inmemory_analyzer
from data_platform.analyzer.analyzer_chain import AnalyzerChain
from data_platform.cleaner import inmemory_cleaner
from data_platform.cleaner.cleaner_chain import CleanerChain
from data_platform.config.key import Key
from data_platform.config.pipeline_type import PipelineType
from data_platform.domain.online_shopping.online_shopping_attribute_model import OnlineShoppingAttributeModel
from data_platform.enricher import inmemory_enricher
from data_platform.enricher.enricher_chain import EnricherChain
from data_platform.ingestion.rest_api_csv_ingestor import RestApiCsvIngestor
from data_platform.model.aggregate_model import AggregateModel
from data_platform.model.dataframe_model import DataFrameModel
from data_platform.model.dataset_model import DatasetModel
from data_platform.model.pipeline_flow_model import PipelineFlowModel
from data_platform.registry.endpoint_registry import endpoint_registry
from data_platform.repository.data_exposer import DataExposer
from data_platform.repository.inmemory_database_repository import InmemoryDatabaseRepository
from data_platform.repository.inmemory_datalake_repository import InmemoryDatalakeRepository
from data_platform.repository.inmemory_warehouse_repository import InmemoryWarehouseRepository
from data_platform.validator import inmemory_validator
from data_platform.validator.validator_chain import ValidatorChain

attribute = OnlineShoppingAttributeModel()

ENDPOINT_KEYS = (
    Key.ONLINE_SHOPPING_REST_API,
    Key.ONLINE_SHOPPING_KAFKA_CONSUMER,
    Key.ONLINE_SHOPPING_DATA_LAKE,
    Key.ONLINE_SHOPPING_BACKUP_DATA_LAKE,
    Key.ONLINE_SHOPPING_DATABASE,
    Key.ONLINE_SHOPPING_WAREHOUSE,
)

REQUIRED_COLUMNS = frozenset({
    attribute.order_id,
    attribute.order_date,
    attribute.sales_channel,
    attribute.country,
    attribute.product_name,
    attribute.unit_price,
    attribute.quantity,
    attribute.total_amount,
})


def create_online_shopping_dataset(pipeline_type: PipelineType) -> DatasetModel:
    if pipeline_type == PipelineType.SPARK:
        return _create_spark_dataset()
    return _create_inmemory_dataset()


def _create_inmemory_dataset() -> DatasetModel:
    endpoints = {key: endpoint_registry.get_item(key) for key in ENDPOINT_KEYS}
    return DatasetModel(
        name="online_shopping",
        audit=endpoint_registry.get_item(Key.AUDIT),
        dataframe=DataFrameModel(required_columns=REQUIRED_COLUMNS),
        endpoints=endpoints,
        flow=PipelineFlowModel(
            repository=InmemoryDatalakeRepository(endpoints[Key.ONLINE_SHOPPING_DATA_LAKE]),
            backup_repository=InmemoryDatalakeRepository(endpoints[Key.ONLINE_SHOPPING_BACKUP_DATA_LAKE]),
            ingestors=(RestApiCsvIngestor(endpoints[Key.ONLINE_SHOPPING_REST_API]),),
            cleaners=CleanerChain(_cleaners(inmemory_cleaner)),
            validators=ValidatorChain(_validators(inmemory_validator)),
            enrichers=EnricherChain(_enrichers(inmemory_enricher)),
            exposers=(
                DataExposer((
                    InmemoryDatabaseRepository(endpoints[Key.ONLINE_SHOPPING_DATABASE]).overwrite,
                    InmemoryWarehouseRepository(endpoints[Key.ONLINE_SHOPPING_WAREHOUSE]).overwrite,
                )),
            ),
            analyzers=AnalyzerChain(_analyzers(inmemory_analyzer)),
        ),
    )


def _create_spark_dataset() -> DatasetModel:
    from data_platform.analyzer import spark_analyzer
    from data_platform.cleaner import spark_cleaner
    from data_platform.connector.spark_connector import create_session
    from data_platform.enricher import spark_enricher
    from data_platform.ingestion.spark_kafka_ingestor import SparkKafkaIngestor
    from data_platform.repository.spark_database_repository import SparkDatabaseRepository
    from data_platform.repository.spark_datalake_repository import SparkDatalakeRepository
    from data_platform.repository.spark_warehouse_repository import SparkWarehouseRepository
    from data_platform.validator import spark_validator

    endpoints = {key: endpoint_registry.get_item(key) for key in ENDPOINT_KEYS}
    schema = attribute.spark_schema()
    return DatasetModel(
        name="online_shopping",
        audit=endpoint_registry.get_item(Key.AUDIT),
        dataframe=DataFrameModel(schema=schema, required_columns=REQUIRED_COLUMNS),
        endpoints=endpoints,
        flow=PipelineFlowModel(
            repository=SparkDatalakeRepository(create_session, endpoints[Key.ONLINE_SHOPPING_DATA_LAKE]),
            backup_repository=SparkDatalakeRepository(create_session, endpoints[Key.ONLINE_SHOPPING_BACKUP_DATA_LAKE]),
            ingestors=(SparkKafkaIngestor(endpoints[Key.ONLINE_SHOPPING_KAFKA_CONSUMER], create_session, schema),),
            cleaners=CleanerChain(_cleaners(spark_cleaner)),
            validators=spark_validator.SparkValidatorChain(_validators(spark_validator)),
            enrichers=EnricherChain(_enrichers(spark_enricher)),
            exposers=(
                DataExposer((
                    SparkDatabaseRepository(endpoints[Key.ONLINE_SHOPPING_DATABASE]).overwrite,
                    SparkWarehouseRepository(endpoints[Key.ONLINE_SHOPPING_WAREHOUSE]).overwrite,
                )),
            ),
            analyzers=AnalyzerChain(_analyzers(spark_analyzer)),
        ),
    )


def _cleaners(cleaner: ModuleType) -> tuple:
    numeric_columns = (
        attribute.customer_id,
        attribute.unit_price,
        attribute.quantity,
        attribute.subtotal,
        attribute.discount_percent,
        attribute.shipping_cost,
        attribute.tax_amount,
        attribute.total_amount,
        attribute.delivery_days,
    )
    return (
        cleaner.DropDuplicatesCleaner(attribute.order_id),
        cleaner.ToDatetimeCleaner(attribute.order_date),
        cleaner.ToDatetimeCleaner(attribute.estimated_delivery_date),
        cleaner.StripColumnCleaner(attribute.phone),
        *(cleaner.NumericColumnCleaner(column) for column in numeric_columns),
    )


def _validators(validator: ModuleType) -> tuple:
    return (
        validator.RequiredColumnsValidator((
            attribute.order_id,
            attribute.order_date,
            attribute.quantity,
            attribute.unit_price,
            attribute.total_amount,
        )),
        validator.NotNullValidator(attribute.order_id),
        validator.NotNullValidator(attribute.order_date),
        validator.PositiveValidator(attribute.quantity),
        validator.NonNegativeValidator(attribute.unit_price),
        validator.NonNegativeValidator(attribute.total_amount),
    )


def _enrichers(enricher: ModuleType) -> tuple:
    return (
        enricher.PercentageEnricher(attribute.subtotal, attribute.discount_percent, attribute.discount_amount),
        enricher.CopyColumnEnricher(attribute.total_amount, attribute.net_revenue, decimals=2),
        enricher.DatetimePartEnricher(attribute.order_date, "year", attribute.year),
        enricher.DatetimePartEnricher(attribute.order_date, "month", attribute.month),
    )


def _analyzers(analyzer: ModuleType) -> tuple:
    return (
        analyzer.GroupAggregateAnalyzer(
            "revenue_by_country",
            AggregateModel(attribute.country, attribute.net_revenue, "sum", "revenue"),
        ),
        analyzer.GroupAggregateAnalyzer(
            "revenue_by_sales_channel",
            AggregateModel(attribute.sales_channel, attribute.net_revenue, "sum", "revenue"),
        ),
        analyzer.GroupAggregateAnalyzer(
            "order_count_by_country",
            AggregateModel(attribute.country, attribute.order_id, "count", "order_count"),
        ),
        analyzer.GroupAggregateAnalyzer(
            "revenue_by_category",
            AggregateModel(attribute.category, attribute.net_revenue, "sum", "revenue"),
        ),
        analyzer.GroupAggregateAnalyzer(
            "average_order_value_by_sales_channel",
            AggregateModel(attribute.sales_channel, attribute.total_amount, "mean", "average_order_value"),
        ),
        analyzer.GroupAggregateAnalyzer(
            "average_delivery_days_by_shipping_method",
            AggregateModel(attribute.shipping_method, attribute.delivery_days, "mean", "average_delivery_days"),
        ),
        analyzer.GroupAggregateAnalyzer(
            "order_count_by_fulfillment_status",
            AggregateModel(attribute.fulfillment_status, attribute.order_id, "count", "order_count"),
        ),
    )
