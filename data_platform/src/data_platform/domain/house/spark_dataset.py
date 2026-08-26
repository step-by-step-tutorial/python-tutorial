from data_platform.analyzers.aggregate_model import AggregateSpecification
from data_platform.analyzers.spark_analyzer_chain import SparkAnalyzerChain
from data_platform.analyzers.spark_analyzer_impl import GroupAggregateAnalyzer
from data_platform.cleaners.spark_cleaner_chain import SparkCleanerChain
from data_platform.cleaners.spark_cleaner_impl import BooleanColumnCleaner, DropDuplicatesCleaner, NumericColumnCleaner, \
    StripColumnCleaner, ToDatetimeCleaner
from data_platform.config.keys import Key
from data_platform.connector.spark_session_factory import create_session
from data_platform.domain.house.attribute import attribute
from data_platform.domain.house.dataset import boolean_columns, date_columns, numeric_columns, text_columns
from data_platform.domain.house.spark_schema import HOUSE_SCHEMA
from data_platform.enrichers.spark_enricher_chain import SparkEnricherChain
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
from data_platform.validators.spark_validator_impl import NotNullValidator, PositiveValidator, RequiredColumnsValidator

spark_house_dataset = Dataset(
    name="house",
    audit=endpoint_registry.get_item("audit"),
    dataframe=DataFrameModel(schema=HOUSE_SCHEMA, required_columns=frozenset(attribute.columns)),
    endpoints={
        Key.HOUSE_REST_API: endpoint_registry.get_item(Key.HOUSE_REST_API),
        Key.HOUSE_DATA_LAKE: endpoint_registry.get_item(Key.HOUSE_DATA_LAKE),
        Key.HOUSE_BACKUP_DATA_LAKE: endpoint_registry.get_item(Key.HOUSE_BACKUP_DATA_LAKE),
        Key.HOUSE_DATABASE: endpoint_registry.get_item(Key.HOUSE_DATABASE),
        Key.HOUSE_WAREHOUSE: endpoint_registry.get_item(Key.HOUSE_WAREHOUSE),
    },
    flow=SparkPipelineFlow(
        repository=SparkDatalakeRepository(create_session, endpoint_registry.get_item(Key.HOUSE_DATA_LAKE)),
        backup_repository=SparkDatalakeRepository(create_session, endpoint_registry.get_item(Key.HOUSE_BACKUP_DATA_LAKE)),
        ingestors=(SparkRestApiCsvIngestor(endpoint_registry.get_item(Key.HOUSE_REST_API), create_session, HOUSE_SCHEMA),),
        cleaners=SparkCleanerChain(
            tuple(NumericColumnCleaner(column) for column in numeric_columns)
            + tuple(BooleanColumnCleaner(column) for column in boolean_columns)
            + tuple(ToDatetimeCleaner(column) for column in date_columns)
            + tuple(StripColumnCleaner(column) for column in text_columns)
            + (DropDuplicatesCleaner(attribute.property_id),)
        ),
        validators=SparkValidatorChain(
            (RequiredColumnsValidator(attribute.columns), NotNullValidator(attribute.property_id),
             NotNullValidator(attribute.area_sqm), NotNullValidator(attribute.total_price),
             PositiveValidator(attribute.area_sqm), PositiveValidator(attribute.total_price))),
        enrichers=SparkEnricherChain(),
        exposers=(DataExposer((SparkDatabaseRepository(endpoint_registry.get_item(Key.HOUSE_DATABASE)).overwrite,)),
                  DataExposer((SparkWarehouseRepository(endpoint_registry.get_item(Key.HOUSE_WAREHOUSE)).overwrite,))),
        analyzers=SparkAnalyzerChain((
            GroupAggregateAnalyzer("property_count_by_city",
                                   AggregateSpecification(attribute.city, attribute.property_id, "count",
                                                          "property_count")),
            GroupAggregateAnalyzer("average_total_price_by_city",
                                   AggregateSpecification(attribute.city, attribute.total_price, "avg",
                                                          "average_total_price")),
            GroupAggregateAnalyzer("average_price_per_square_meter_by_property_type",
                                   AggregateSpecification(attribute.property_type, attribute.price_per_sqm, "avg",
                                                          "average_price_per_sqm")),
            GroupAggregateAnalyzer("average_living_area_by_property_type",
                                   AggregateSpecification(attribute.property_type, attribute.living_area_sqm, "avg",
                                                          "average_living_area_sqm")),
            GroupAggregateAnalyzer("average_energy_consumption_by_city",
                                   AggregateSpecification(attribute.city, attribute.annual_energy_consumption_kwh,
                                                          "avg", "average_energy_consumption_kwh")),
        )),
    ),
)
