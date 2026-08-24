from data_platform.config.keys import Key
from data_platform.config.main_settings import settings as main_settings
from data_platform.domain.house.attribute import HOUSE_ATTRIBUTE as columns
from data_platform.domain.house.data_warehouse_analyzer import (
    DataWarehouseHouseAnalyzer,
)
from data_platform.domain.house.inmemory_analyzer import InmemoryHouseAnalyzer
from data_platform.domain.house.inmemory_transformer import InmemoryHouseTransformer
from data_platform.domain.house.spark_schema import build_schema
from data_platform.ingestion.csv_file_ingestor import CsvFileIngestor
from data_platform.model import (
    DataFrameModel,
    DataLakeEndpoint,
    DataWarehouseEndpoint,
    DatabaseEndpoint,
    Dataset,
    FileEndpoint,
    MessagingEndpoint,
    PipelineSteps,
)
from data_platform.persistence.data_lake_repository import DataLakeRepository
from data_platform.persistence.inmemory_data_warehouse_repository import (
    PandasDataWarehouseRepository,
)
from data_platform.persistence.inmemory_database_repository import (
    PandasDatabaseRepository,
)
from data_platform.persistence.repository_data_exposer import RepositoryDataExposer
from data_platform.presentation.dataframe_display import show_map_of_dataframe
from data_platform.registry.endpoint_registry import audit_endpoint, endpoint_registry
from data_platform.service.data_warehouse_analysis_service import DataWarehouseAnalyzer
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
    audit=endpoint_registry.get_item(audit_endpoint.name),
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
        Key.HOUSE_DATA_WAREHOUSE: DataWarehouseEndpoint(
            name=Key.HOUSE_DATA_WAREHOUSE,
            connection_name=Key.HOUSE_DATA_WAREHOUSE,
            schema=main_settings.data_warehouse[Key.HOUSE_DATA_WAREHOUSE].database_name,
            table_name="house_table",
            full_table_name=f"{main_settings.data_warehouse[Key.HOUSE_DATA_WAREHOUSE].database_name}.house_table",
            create_sql_files={
                "create_database": "datawarehouse/house/create_database.sql",
                "create_table": "datawarehouse/house/create_table.sql",
            },
            truncate_sql_files={
                "truncate": "datawarehouse/house/truncate_datawarehouse.sql"
            },
            query_sql_files={
                "select_all": "datawarehouse/select_all.sql",
                "average_price_by_address": "datawarehouse/house/select_average_price_by_address.sql",
                "average_price_per_square_meter_by_room": "datawarehouse/house/select_average_price_per_square_meter_by_room.sql",
            },
        ),
    },
    pipeline_steps=PipelineSteps(
        storages=(
            DataLakeRepository(
                DataLakeEndpoint(
                    name=Key.HOUSE_DATA_LAKE,
                    connection_name=Key.HOUSE_DATA_LAKE,
                    bucket_name=main_settings.data_lake[
                        Key.HOUSE_DATA_LAKE
                    ].bucket_name,
                    scheme=main_settings.data_lake[Key.HOUSE_DATA_LAKE].scheme,
                )
            ),
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
        cleaners=(InmemoryHouseTransformer(),),
        enrichers=(InmemoryHouseTransformer(),),
        exposers=(
            RepositoryDataExposer(
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
            ),
            RepositoryDataExposer(
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
                PandasDataWarehouseRepository(
                    DataWarehouseEndpoint(
                        name=Key.HOUSE_DATA_WAREHOUSE,
                        connection_name=Key.HOUSE_DATA_WAREHOUSE,
                        schema=main_settings.data_warehouse[
                            Key.HOUSE_DATA_WAREHOUSE
                        ].database_name,
                        table_name="house_table",
                        full_table_name=f"{main_settings.data_warehouse[Key.HOUSE_DATA_WAREHOUSE].database_name}.house_table",
                        create_sql_files={
                            "create_database": "datawarehouse/house/create_database.sql",
                            "create_table": "datawarehouse/house/create_table.sql",
                        },
                        truncate_sql_files={
                            "truncate": "datawarehouse/house/truncate_datawarehouse.sql"
                        },
                        query_sql_files={
                            "select_all": "datawarehouse/select_all.sql",
                            "average_price_by_address": "datawarehouse/house/select_average_price_by_address.sql",
                            "average_price_per_square_meter_by_room": "datawarehouse/house/select_average_price_per_square_meter_by_room.sql",
                        },
                    )
                ).replace,
            ),
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
            DataWarehouseAnalyzer(
                PandasDataWarehouseRepository(
                    DataWarehouseEndpoint(
                        name=Key.HOUSE_DATA_WAREHOUSE,
                        connection_name=Key.HOUSE_DATA_WAREHOUSE,
                        schema=main_settings.data_warehouse[
                            Key.HOUSE_DATA_WAREHOUSE
                        ].database_name,
                        table_name="house_table",
                        full_table_name=f"{main_settings.data_warehouse[Key.HOUSE_DATA_WAREHOUSE].database_name}.house_table",
                        create_sql_files={
                            "create_database": "datawarehouse/house/create_database.sql",
                            "create_table": "datawarehouse/house/create_table.sql",
                        },
                        truncate_sql_files={
                            "truncate": "datawarehouse/house/truncate_datawarehouse.sql"
                        },
                        query_sql_files={
                            "select_all": "datawarehouse/select_all.sql",
                            "average_price_by_address": "datawarehouse/house/select_average_price_by_address.sql",
                            "average_price_per_square_meter_by_room": "datawarehouse/house/select_average_price_per_square_meter_by_room.sql",
                        },
                    )
                ),
                DataWarehouseHouseAnalyzer(),
                show_map_of_dataframe,
            ),
        ),
    ),
)
