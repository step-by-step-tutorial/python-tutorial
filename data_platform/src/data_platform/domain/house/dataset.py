from data_platform.analyzers.aggregate_model import AggregateSpecification
from data_platform.analyzers.analyzer_chain import AnalyzerChain
from data_platform.analyzers.analyzer_impl import GroupAggregateAnalyzer
from data_platform.cleaners.cleaner_impl import CleanerChain, RenameColumnsCleaner, NumericColumnCleaner, \
    BooleanColumnCleaner, StripColumnCleaner, DropDuplicatesCleaner
from data_platform.config.keys import Key
from data_platform.domain.house.attribute import attribute
from data_platform.domain.house.spark_schema import build_schema
from data_platform.enrichers.enricher_impl import DivideColumnsEnricher, EnricherChain, HashColumnsEnricher
from data_platform.ingestion.csv_file_ingestor import CsvFileIngestor
from data_platform.model.dataframe_model import DataFrameModel
from data_platform.model.dataset import Dataset
from data_platform.model.pipeline_flow import PipelineFlow
from data_platform.registry.endpoint_registry import endpoint_registry
from data_platform.repository.inmemory_datalake_repository import DataLakeRepository
from data_platform.repository.inmemory_database_repository import (
    InmemoryDataframeRepository,
)
from data_platform.repository.inmemory_warehouse_repository import (
    InmemoryWarehouseRepository,
)
from data_platform.repository.data_exposer import DataExposer
from data_platform.validators.validator_impl import (
    NonNegativeValidator,
    NotNullValidator,
    PositiveValidator,
    RequiredColumnsValidator,
)
from data_platform.validators.validator_chain import ValidatorChain

house_dataset = Dataset(
    name="house",
    dataframe=DataFrameModel(
        schema=build_schema(),
        required_columns=frozenset(
            {
                attribute.area_raw,
                attribute.room_raw,
                attribute.parking_raw,
                attribute.warehouse_raw,
                attribute.elevator_raw,
                attribute.address_raw,
                attribute.price_raw,
                attribute.price_usd_raw,
            }
        ),
    ),
    audit=endpoint_registry.get_item("audit"),
    endpoints={
        Key.HOUSE_CSV_FILE: endpoint_registry.get_item(Key.HOUSE_CSV_FILE),
        Key.HOUSE_KAFKA_CONSUMER: endpoint_registry.get_item(Key.HOUSE_KAFKA_CONSUMER),
        Key.HOUSE_KAFKA_PRODUCER: endpoint_registry.get_item(Key.HOUSE_KAFKA_PRODUCER),
        Key.HOUSE_DATA_LAKE: endpoint_registry.get_item(Key.HOUSE_DATA_LAKE),
        Key.HOUSE_DATABASE: endpoint_registry.get_item(Key.HOUSE_DATABASE),
        Key.HOUSE_WAREHOUSE: endpoint_registry.get_item(Key.HOUSE_WAREHOUSE),
    },
    flow=PipelineFlow(
        repository=DataLakeRepository(
            endpoint_registry.get_item(Key.HOUSE_DATA_LAKE)
        ),
        ingestors=(
            CsvFileIngestor(
                endpoint_registry.get_item(Key.HOUSE_CSV_FILE)
            ),
        ),
        cleaners=CleanerChain((
            RenameColumnsCleaner({
                attribute.area_raw: attribute.area, attribute.room_raw: attribute.room,
                attribute.parking_raw: attribute.parking, attribute.warehouse_raw: attribute.warehouse,
                attribute.elevator_raw: attribute.elevator, attribute.address_raw: attribute.address,
                attribute.price_raw: attribute.price, attribute.price_usd_raw: attribute.price_usd,
            }),
            NumericColumnCleaner(attribute.area),
            NumericColumnCleaner(attribute.room),
            NumericColumnCleaner(attribute.price),
            NumericColumnCleaner(attribute.price_usd),
            BooleanColumnCleaner(attribute.parking),
            BooleanColumnCleaner(attribute.warehouse),
            BooleanColumnCleaner(attribute.elevator),
            StripColumnCleaner(attribute.address),
            DropDuplicatesCleaner(),
        )),
        validators=ValidatorChain((
            RequiredColumnsValidator((attribute.area, attribute.room, attribute.price)),
            NotNullValidator(attribute.area), NotNullValidator(attribute.room),
            NotNullValidator(attribute.price), PositiveValidator(attribute.area),
            NonNegativeValidator(attribute.room), PositiveValidator(attribute.price),
        )),
        enrichers=EnricherChain((
            DivideColumnsEnricher(attribute.price, attribute.area, attribute.price_per_square_meter),
            DivideColumnsEnricher(attribute.price_usd, attribute.area, attribute.price_usd_per_square_meter),
            HashColumnsEnricher((
                attribute.area, attribute.room, attribute.parking, attribute.warehouse,
                attribute.elevator, attribute.address, attribute.price, attribute.price_usd,
            ), attribute.listing_key),
        )),
        exposers=(
            DataExposer((
                InmemoryDataframeRepository(
                    endpoint_registry.get_item(Key.HOUSE_DATABASE)
                ).overwrite,
            )),
            DataExposer((
                InmemoryWarehouseRepository(
                    endpoint_registry.get_item(Key.HOUSE_WAREHOUSE)
                ).overwrite,
            )),
        ),
        analyzers=AnalyzerChain((
            GroupAggregateAnalyzer("average_price_by_address",
                                   AggregateSpecification(attribute.address, attribute.price, "mean", "average_price")),
            GroupAggregateAnalyzer("average_price_per_square_meter_by_room",
                                   AggregateSpecification(attribute.room, attribute.price_per_square_meter, "mean",
                                                          "average_price_per_square_meter")),
        )),
    ),
)
