from types import ModuleType

from data_platform.analyzer import inmemory_analyzer
from data_platform.analyzer.analyzer_chain import AnalyzerChain
from data_platform.cleaner import inmemory_cleaner
from data_platform.cleaner.cleaner_chain import CleanerChain
from data_platform.config.key import Key
from data_platform.config.pipeline_type import PipelineType
from data_platform.domain.house.house_attribute_model import HouseAttributeModel
from data_platform.ingestion.rest_api_csv_ingestor import RestApiCsvIngestor
from data_platform.model.aggregate_model import AggregateModel
from data_platform.model.attribute_model import ColumnType
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

attribute = HouseAttributeModel()

ENDPOINT_KEYS = (
    Key.HOUSE_CSV_FILE,
    Key.HOUSE_REST_API,
    Key.HOUSE_KAFKA_CONSUMER,
    Key.HOUSE_KAFKA_PRODUCER,
    Key.HOUSE_DATA_LAKE,
    Key.HOUSE_BACKUP_DATA_LAKE,
    Key.HOUSE_DATABASE,
    Key.HOUSE_WAREHOUSE,
)


def create_house_dataset(pipeline_type: PipelineType) -> DatasetModel:
    if pipeline_type == PipelineType.SPARK:
        return _create_spark_dataset()
    return _create_inmemory_dataset()


def _create_inmemory_dataset() -> DatasetModel:
    endpoints = {key: endpoint_registry.get_item(key) for key in ENDPOINT_KEYS}
    return DatasetModel(
        name="house",
        audit=endpoint_registry.get_item(Key.AUDIT),
        dataframe=DataFrameModel(required_columns=frozenset(attribute.columns)),
        endpoints=endpoints,
        flow=PipelineFlowModel(
            repository=InmemoryDatalakeRepository(endpoints[Key.HOUSE_DATA_LAKE]),
            backup_repository=InmemoryDatalakeRepository(endpoints[Key.HOUSE_BACKUP_DATA_LAKE]),
            ingestors=(RestApiCsvIngestor(endpoints[Key.HOUSE_REST_API]),),
            cleaners=CleanerChain(_cleaners(inmemory_cleaner)),
            validators=ValidatorChain(_validators(inmemory_validator)),
            exposers=(
                DataExposer((InmemoryDatabaseRepository(endpoints[Key.HOUSE_DATABASE]).overwrite,)),
                DataExposer((InmemoryWarehouseRepository(endpoints[Key.HOUSE_WAREHOUSE]).overwrite,)),
            ),
            analyzers=AnalyzerChain(_analyzers(inmemory_analyzer)),
        ),
    )


def _create_spark_dataset() -> DatasetModel:
    from data_platform.analyzer import spark_analyzer
    from data_platform.cleaner import spark_cleaner
    from data_platform.connector.spark_connector import create_session
    from data_platform.ingestion.spark_rest_api_csv_ingestor import SparkRestApiCsvIngestor
    from data_platform.repository.spark_database_repository import SparkDatabaseRepository
    from data_platform.repository.spark_datalake_repository import SparkDatalakeRepository
    from data_platform.repository.spark_warehouse_repository import SparkWarehouseRepository
    from data_platform.validator import spark_validator

    endpoints = {key: endpoint_registry.get_item(key) for key in ENDPOINT_KEYS}
    schema = attribute.spark_schema()
    return DatasetModel(
        name="house",
        audit=endpoint_registry.get_item(Key.AUDIT),
        dataframe=DataFrameModel(schema=schema, required_columns=frozenset(attribute.columns)),
        endpoints=endpoints,
        flow=PipelineFlowModel(
            repository=SparkDatalakeRepository(create_session, endpoints[Key.HOUSE_DATA_LAKE]),
            backup_repository=SparkDatalakeRepository(create_session, endpoints[Key.HOUSE_BACKUP_DATA_LAKE]),
            ingestors=(SparkRestApiCsvIngestor(endpoints[Key.HOUSE_REST_API], create_session, schema),),
            cleaners=CleanerChain(_cleaners(spark_cleaner)),
            validators=spark_validator.SparkValidatorChain(_validators(spark_validator)),
            exposers=(
                DataExposer((SparkDatabaseRepository(endpoints[Key.HOUSE_DATABASE]).overwrite,)),
                DataExposer((SparkWarehouseRepository(endpoints[Key.HOUSE_WAREHOUSE]).overwrite,)),
            ),
            analyzers=AnalyzerChain(_analyzers(spark_analyzer)),
        ),
    )


def _cleaners(cleaner: ModuleType) -> tuple:
    numeric_columns = attribute.columns_of(ColumnType.DOUBLE, ColumnType.INTEGER)
    boolean_columns = attribute.columns_of(ColumnType.BOOLEAN)
    date_columns = attribute.columns_of(ColumnType.DATE, ColumnType.TIMESTAMP)
    text_columns = attribute.columns_of(ColumnType.STRING)
    return (
        tuple(cleaner.NumericColumnCleaner(column) for column in numeric_columns)
        + tuple(cleaner.BooleanColumnCleaner(column) for column in boolean_columns)
        + tuple(cleaner.ToDatetimeCleaner(column) for column in date_columns)
        + tuple(cleaner.StripColumnCleaner(column) for column in text_columns)
        + (cleaner.DropDuplicatesCleaner(attribute.property_id),)
    )


def _validators(validator: ModuleType) -> tuple:
    return (
        validator.RequiredColumnsValidator(attribute.columns),
        validator.NotNullValidator(attribute.property_id),
        validator.NotNullValidator(attribute.area_sqm),
        validator.NotNullValidator(attribute.total_price),
        validator.PositiveValidator(attribute.area_sqm),
        validator.PositiveValidator(attribute.total_price),
    )


def _analyzers(analyzer: ModuleType) -> tuple:
    return (
        analyzer.GroupAggregateAnalyzer(
            "property_count_by_city",
            AggregateModel(attribute.city, attribute.property_id, "count", "property_count"),
        ),
        analyzer.GroupAggregateAnalyzer(
            "average_total_price_by_city",
            AggregateModel(attribute.city, attribute.total_price, "mean", "average_total_price"),
        ),
        analyzer.GroupAggregateAnalyzer(
            "average_price_per_square_meter_by_property_type",
            AggregateModel(attribute.property_type, attribute.price_per_sqm, "mean", "average_price_per_sqm"),
        ),
        analyzer.GroupAggregateAnalyzer(
            "average_living_area_by_property_type",
            AggregateModel(attribute.property_type, attribute.living_area_sqm, "mean", "average_living_area_sqm"),
        ),
        analyzer.GroupAggregateAnalyzer(
            "average_energy_consumption_by_city",
            AggregateModel(attribute.city, attribute.annual_energy_consumption_kwh, "mean",
                           "average_energy_consumption_kwh"),
        ),
    )
