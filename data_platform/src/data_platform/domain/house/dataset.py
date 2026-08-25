from data_platform.config.keys import Key
from data_platform.config.main_settings import settings as main_settings
from data_platform.domain.house.attribute import HOUSE_ATTRIBUTE as columns
from data_platform.domain.house.warehouse_analyzer import (
    WarehouseHouseAnalyzer,
)
from data_platform.domain.house.inmemory_analyzer import InmemoryHouseAnalyzer
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
    DataLakeEndpoint,
    WarehouseEndpoint,
    DatabaseEndpoint,
    Dataset,
    FileEndpoint,
    MessagingEndpoint,
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
from data_platform.presentation.dataframe_display import show_map_of_dataframe
from data_platform.registry.endpoint_registry import audit_endpoint, endpoint_registry
from data_platform.service.warehouse_analysis_service import WarehouseAnalyzer
from data_platform.service.dataframe_analysis_service import DataFrameAnalyzer

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
    audit=endpoint_registry.get_item(audit_endpoint.pipeline_name),
    endpoints={
        Key.HOUSE_CSV_FILE: FileEndpoint(
            name=Key.HOUSE_CSV_FILE,
            file_name="house.csv",
            file_path=str(
                main_settings.app.root / main_settings.app.resources_dir / "house.csv"
            ),
        ),
        Key.HOUSE_KAFKA_CONSUMER: MessagingEndpoint(
            name=Key.HOUSE_KAFKA_CONSUMER,
            connection_name=Key.HOUSE_KAFKA_CONSUMER,
            channel_name=main_settings.messaging[Key.HOUSE_KAFKA_CONSUMER].channel_name,
            bootstrap_servers=main_settings.messaging[
                Key.HOUSE_KAFKA_CONSUMER
            ].bootstrap_servers,
            starting_offsets=main_settings.messaging[
                Key.HOUSE_KAFKA_CONSUMER
            ].starting_offsets,
        ),
        Key.HOUSE_KAFKA_PRODUCER: MessagingEndpoint(
            name=Key.HOUSE_KAFKA_PRODUCER,
            connection_name=Key.HOUSE_KAFKA_PRODUCER,
            channel_name=main_settings.messaging[Key.HOUSE_KAFKA_CONSUMER].channel_name,
            bootstrap_servers=main_settings.messaging[
                Key.HOUSE_KAFKA_PRODUCER
            ].bootstrap_servers,
        ),
        Key.HOUSE_DATA_LAKE: DataLakeEndpoint(
            name=Key.HOUSE_DATA_LAKE,
            connection_name=Key.HOUSE_DATA_LAKE,
            bucket_name=main_settings.data_lake[Key.HOUSE_DATA_LAKE].bucket_name,
            scheme=main_settings.data_lake[Key.HOUSE_DATA_LAKE].scheme,
        ),
        Key.HOUSE_DATABASE: DatabaseEndpoint(
            name=Key.HOUSE_DATABASE,
            connection_name=Key.HOUSE_DATABASE,
            schema="house",
            stage_table_name="house_stage",
            full_stage_table_name="house.house_stage",
            table_names=["house.house_stage"],
            create_sql_files={"create": "database/house/create_tables.sql"},
            truncate_sql_files={"truncate": "database/house/truncate_stage.sql"},
            query_sql_files={"select_all": "database/select_all.sql"},
        ),
        Key.HOUSE_WAREHOUSE: WarehouseEndpoint(
            name=Key.HOUSE_WAREHOUSE,
            connection_name=Key.HOUSE_WAREHOUSE,
            schema=main_settings.warehouse[Key.HOUSE_WAREHOUSE].database_name,
            table_name="house_table",
            full_table_name=f"{main_settings.warehouse[Key.HOUSE_WAREHOUSE].database_name}.house_table",
            create_sql_files={
                "create_database": "warehouse/house/create_database.sql",
                "create_table": "warehouse/house/create_table.sql",
            },
            truncate_sql_files={
                "truncate": "warehouse/house/truncate_warehouse.sql"
            },
            query_sql_files={
                "select_all": "warehouse/select_all.sql",
                "average_price_by_address": "warehouse/house/select_average_price_by_address.sql",
                "average_price_per_square_meter_by_room": "warehouse/house/select_average_price_per_square_meter_by_room.sql",
            },
        ),
    },
    flow=PipelineFlow(
        repository=DataLakeRepository(
            DataLakeEndpoint(
                name=Key.HOUSE_DATA_LAKE,
                connection_name=Key.HOUSE_DATA_LAKE,
                bucket_name=main_settings.data_lake[
                    Key.HOUSE_DATA_LAKE
                ].bucket_name,
                scheme=main_settings.data_lake[Key.HOUSE_DATA_LAKE].scheme,
            )
        ),
        ingestors=(
            CsvFileIngestor(
                FileEndpoint(
                    name=Key.HOUSE_CSV_FILE,
                    file_name="house.csv",
                    file_path=str(
                        main_settings.app.root
                        / main_settings.app.resources_dir
                        / "house.csv"
                    ),
                )
            ),
        ),
        cleaner=CleanerChain((
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
        validator=ValidatorChain((
            RequiredColumnsValidator((columns.area, columns.room, columns.price)),
            NotNullValidator(columns.area), NotNullValidator(columns.room),
            NotNullValidator(columns.price), PositiveValidator(columns.area),
            NonNegativeValidator(columns.room), PositiveValidator(columns.price),
        )),
        enricher=EnricherChain((
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
                    DatabaseEndpoint(
                        name=Key.HOUSE_DATABASE,
                        connection_name=Key.HOUSE_DATABASE,
                        schema="house",
                        stage_table_name="house_stage",
                        full_stage_table_name="house.house_stage",
                        table_names=["house.house_stage"],
                        create_sql_files={"create": "database/house/create_tables.sql"},
                        truncate_sql_files={
                            "truncate": "database/house/truncate_stage.sql"
                        },
                        query_sql_files={"select_all": "database/select_all.sql"},
                    )
                ).replace,
            )),
            RepositoryDataExposer((
                PandasWarehouseRepository(
                    WarehouseEndpoint(
                        name=Key.HOUSE_WAREHOUSE,
                        connection_name=Key.HOUSE_WAREHOUSE,
                        schema=main_settings.warehouse[
                            Key.HOUSE_WAREHOUSE
                        ].database_name,
                        table_name="house_table",
                        full_table_name=f"{main_settings.warehouse[Key.HOUSE_WAREHOUSE].database_name}.house_table",
                        create_sql_files={
                            "create_database": "warehouse/house/create_database.sql",
                            "create_table": "warehouse/house/create_table.sql",
                        },
                        truncate_sql_files={
                            "truncate": "warehouse/house/truncate_warehouse.sql"
                        },
                        query_sql_files={
                            "select_all": "warehouse/select_all.sql",
                            "average_price_by_address": "warehouse/house/select_average_price_by_address.sql",
                            "average_price_per_square_meter_by_room": "warehouse/house/select_average_price_per_square_meter_by_room.sql",
                        },
                    )
                ).replace,
            )),
        ),
        analyzers=(
            DataFrameAnalyzer(
                DataLakeRepository(
                    DataLakeEndpoint(
                        name=Key.HOUSE_DATA_LAKE,
                        connection_name=Key.HOUSE_DATA_LAKE,
                        bucket_name=main_settings.data_lake[
                            Key.HOUSE_DATA_LAKE
                        ].bucket_name,
                        scheme=main_settings.data_lake[Key.HOUSE_DATA_LAKE].scheme,
                    )
                ).find,
                InmemoryHouseAnalyzer(),
                show_map_of_dataframe,
            ),
            WarehouseAnalyzer(
                PandasWarehouseRepository(
                    WarehouseEndpoint(
                        name=Key.HOUSE_WAREHOUSE,
                        connection_name=Key.HOUSE_WAREHOUSE,
                        schema=main_settings.warehouse[
                            Key.HOUSE_WAREHOUSE
                        ].database_name,
                        table_name="house_table",
                        full_table_name=f"{main_settings.warehouse[Key.HOUSE_WAREHOUSE].database_name}.house_table",
                        create_sql_files={
                            "create_database": "warehouse/house/create_database.sql",
                            "create_table": "warehouse/house/create_table.sql",
                        },
                        truncate_sql_files={
                            "truncate": "warehouse/house/truncate_warehouse.sql"
                        },
                        query_sql_files={
                            "select_all": "warehouse/select_all.sql",
                            "average_price_by_address": "warehouse/house/select_average_price_by_address.sql",
                            "average_price_per_square_meter_by_room": "warehouse/house/select_average_price_per_square_meter_by_room.sql",
                        },
                    )
                ),
                WarehouseHouseAnalyzer(),
                show_map_of_dataframe,
            ),
        ),
    ),
)
