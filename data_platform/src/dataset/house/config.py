import dataset.house.model as schema
from app_config import env_config as ec
from dataset.definition import (
    Audit,
    DatabaseConnection,
    Dataset,
    Destination,
    Datalake,
    DataWarehouse,
    FileSource,
    Dataframe,
    Messaging,
    Source,
    StageDatabase,
    Serialization,
)
from dataset.house.inmemory_processor import InmemoryHouseProcessor
from dataset.house.spark_processor import SparkHouseProcessor
from model.house_event import HouseEvent
from util.file_utils import read_text_file

HOUSE_DATASET = Dataset(
    name="house",
    dataframe=Dataframe(
        schema=schema.struct_type,
        required_columns=schema.required_columns,
    ),
    serialization=Serialization(
        event_key_column=schema.model.ADDRESS_RAW,
        event_converter=lambda row: HouseEvent.from_dict(row).to_dict(),
    ),
    messaging=Messaging(
        server=ec.APP_STREAMING_BOOTSTRAP_SERVERS,
        bootstrap_servers=ec.APP_STREAMING_BOOTSTRAP_SERVERS,
        topic="house-events",
        consumer_group="house-spark-consumer",
        checkpoint_path=f"{ec.APP_DATALAKE_SCHEME}://{ec.APP_DATALAKE_BUCKET_NAME}/checkpoints/house-events",
        starting_offsets=ec.APP_STREAMING_STARTING_OFFSETS,
    ),
    audit=Audit(
        topic=ec.APP_STREAMING_AUDIT_TOPIC,
        consumer_group=ec.APP_STREAMING_AUDIT_CONSUMER_GROUP,
        dead_letter_topic=ec.APP_STREAMING_AUDIT_DEAD_LETTER_TOPIC,
        archive_enabled=ec.APP_AUDIT_ARCHIVE_ENABLED,
    ),
    source=Source(
        file=FileSource(
            file_name="house.csv",
            file_path=str(ec.ROOT / ec.RESOURCES_DIR / "house.csv"),
        )
    ),
    destination=Destination(
        datalake=Datalake(bucket_name=ec.APP_DATALAKE_BUCKET_NAME),
        database=StageDatabase(
            connection=DatabaseConnection(
                server=ec.APP_DATABASE_HOST,
                port=ec.APP_DATABASE_PORT,
                database_name=ec.APP_DATABASE_NAME,
                user=ec.APP_DATABASE_USER,
                password=ec.APP_DATABASE_PASSWORD,
                driver=ec.APP_DATABASE_DRIVER,
                jdbc_url=ec.APP_DATABASE_JDBC_URL,
            ),
            table_name="house.house_stage",
            columns=(schema.model.LISTING_KEY, schema.model.AREA,
                     schema.model.ROOM, schema.model.PARKING,
                     schema.model.WAREHOUSE, schema.model.ELEVATOR,
                     schema.model.ADDRESS, schema.model.PRICE,
                     schema.model.PRICE_USD, schema.model.PRICE_PER_SQUARE_METER,
                     schema.model.PRICE_USD_PER_SQUARE_METER),
            before_load_sql_files=("database/house/truncate_stage.sql",),
            after_load_sql_files=(),
        ),
        datawarehouse=DataWarehouse(
            connection=DatabaseConnection(
                server=ec.APP_DATAWAREHOUSE_HOST,
                port=ec.APP_DATAWAREHOUSE_PORT,
                database_name=ec.APP_DATAWAREHOUSE_NAME,
                user=ec.APP_DATAWAREHOUSE_USER,
                password=ec.APP_DATAWAREHOUSE_PASSWORD,
                jdbc_url=f"jdbc:clickhouse://{ec.APP_DATAWAREHOUSE_HOST}:{ec.APP_DATAWAREHOUSE_PORT}/{ec.APP_DATAWAREHOUSE_NAME}",
            ),
            table_name="house_table",
            full_table_name=f"{ec.APP_DATAWAREHOUSE_NAME}.house_table",
            columns=schema.all_columns,
            preparing_sql_files={
                "truncate": read_text_file("datawarehouse/house/truncate_datawarehouse.sql"),
            },
            analysis_sql_files={
                "average_price_by_address": read_text_file("datawarehouse/house/select_average_price_by_address.sql"),
                "average_price_per_square_meter_by_room": read_text_file("datawarehouse/house/select_average_price_per_square_meter_by_room.sql"),
            },
        ),
    ),
    processors={
        "inmemory": InmemoryHouseProcessor(), "spark": SparkHouseProcessor()
    },
)
