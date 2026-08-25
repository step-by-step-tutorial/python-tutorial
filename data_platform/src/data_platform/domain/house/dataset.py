from data_platform.config.keys import Key
from data_platform.config.main_settings import settings as main_settings
from data_platform.domain.house.attribute import HOUSE_ATTRIBUTE as columns
from data_platform.analyzers import AnalyzerChain, GroupAggregateAnalyzer
from data_platform.cleaners import (
    BooleanColumnCleaner,
    CleanerChain,
    DropDuplicatesCleaner,
    NumericColumnCleaner,
    RenameColumnsCleaner,
    StripColumnCleaner,
)
from data_platform.enrichers import DivideColumnsEnricher, EnricherChain, HashColumnsEnricher
from data_platform.validators import (
    NonNegativeValidator,
    NotNullValidator,
    PositiveValidator,
    RequiredColumnsValidator,
    ValidatorChain,
)
from data_platform.domain.house.spark_schema import build_schema
from data_platform.ingestion.csv_file_ingestor import CsvFileIngestor
from data_platform.model import (
    DataFrameModel,
    Dataset,
    PipelineFlow,
)
from data_platform.persistence.data_lake_repository import DataLakeRepository
from data_platform.persistence.inmemory_warehouse_repository import (
    PandasWarehouseRepository,
)
from data_platform.persistence.inmemory_database_repository import (
    PandasDatabaseRepository,
)
from data_platform.persistence.repository_data_exposer import RepositoryDataExposer
from data_platform.registry.endpoint_registry import endpoint_registry

HOUSE_DATASET = Dataset(
    name="house",
    dataframe=DataFrameModel(
        schema=build_schema(),
        required_columns=frozenset(
            {
                columns.area_raw,
                columns.room_raw,
                columns.parking_raw,
                columns.warehouse_raw,
                columns.elevator_raw,
                columns.address_raw,
                columns.price_raw,
                columns.price_usd_raw,
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
                columns.area_raw: columns.area, columns.room_raw: columns.room,
                columns.parking_raw: columns.parking, columns.warehouse_raw: columns.warehouse,
                columns.elevator_raw: columns.elevator, columns.address_raw: columns.address,
                columns.price_raw: columns.price, columns.price_usd_raw: columns.price_usd,
            }),
            NumericColumnCleaner(columns.area),
            NumericColumnCleaner(columns.room),
            NumericColumnCleaner(columns.price),
            NumericColumnCleaner(columns.price_usd),
            BooleanColumnCleaner(columns.parking),
            BooleanColumnCleaner(columns.warehouse),
            BooleanColumnCleaner(columns.elevator),
            StripColumnCleaner(columns.address),
            DropDuplicatesCleaner(),
        )),
        validators=ValidatorChain((
            RequiredColumnsValidator((columns.area, columns.room, columns.price)),
            NotNullValidator(columns.area), NotNullValidator(columns.room),
            NotNullValidator(columns.price), PositiveValidator(columns.area),
            NonNegativeValidator(columns.room), PositiveValidator(columns.price),
        )),
        enrichers=EnricherChain((
            DivideColumnsEnricher(columns.price, columns.area, columns.price_per_square_meter),
            DivideColumnsEnricher(columns.price_usd, columns.area, columns.price_usd_per_square_meter),
            HashColumnsEnricher((
                columns.area, columns.room, columns.parking, columns.warehouse,
                columns.elevator, columns.address, columns.price, columns.price_usd,
            ), columns.listing_key),
        )),
        exposers=(
            RepositoryDataExposer((
                PandasDatabaseRepository(
                    endpoint_registry.get_item(Key.HOUSE_DATABASE)
                ).replace,
            )),
            RepositoryDataExposer((
                PandasWarehouseRepository(
                    endpoint_registry.get_item(Key.HOUSE_WAREHOUSE)
                ).replace,
            )),
        ),
        analyzers=AnalyzerChain((
            GroupAggregateAnalyzer("average_price_by_address", columns.address, columns.price, "mean", "average_price"),
            GroupAggregateAnalyzer("average_price_per_square_meter_by_room", columns.room, columns.price_per_square_meter, "mean", "average_price_per_square_meter"),
        )),
    ),
)
