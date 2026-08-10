import schema
from app_config import env_config as ec
from dataset.definition import StageTable, Dataset, DataWarehouse, Datalake
from dataset.house.inmemory_processor import InmemoryHouseProcessor
from dataset.house.schema import REQUIRED_COLUMNS, DATAFRAME_SCHEMA
from dataset.house.spark_processor import SparkHouseProcessor

HOUSE_DATASET = Dataset(
    name="house",
    file_name="house_data.csv",
    dataframe_schema=DATAFRAME_SCHEMA,
    required_columns=REQUIRED_COLUMNS,
    event_key_column=schema.dataset_model_instance.ADDRESS_RAW,
    streaming_topic="house-events",
    streaming_consumer_group="house-spark-consumer",
    streaming_checkpoint_path=f"{ec.DATALAKE_SCHEME}://{ec.DATALAKE_BUCKET_NAME}/checkpoints/house-events",
    datalake=Datalake(bucket_name=ec.DATALAKE_BUCKET_NAME),
    database=StageTable(
        name="house_stage",
        columns=(schema.dataset_model_instance.LISTING_KEY, schema.dataset_model_instance.AREA,
                 schema.dataset_model_instance.ROOM, schema.dataset_model_instance.PARKING,
                 schema.dataset_model_instance.WAREHOUSE, schema.dataset_model_instance.ELEVATOR,
                 schema.dataset_model_instance.ADDRESS, schema.dataset_model_instance.PRICE,
                 schema.dataset_model_instance.PRICE_USD, schema.dataset_model_instance.PRICE_PER_SQUARE_METER,
                 schema.dataset_model_instance.PRICE_USD_PER_SQUARE_METER),
        before_load_sql_files=("datasets/house/truncate_stage.sql",),
        after_load_sql_files=("datasets/house/upsert_listing.sql",),
    ),
    datawarehouse=DataWarehouse(
        table_name="house_table",
        columns=(schema.dataset_model_instance.LISTING_KEY, schema.dataset_model_instance.AREA,
                 schema.dataset_model_instance.ROOM, schema.dataset_model_instance.PARKING,
                 schema.dataset_model_instance.WAREHOUSE, schema.dataset_model_instance.ELEVATOR,
                 schema.dataset_model_instance.ADDRESS, schema.dataset_model_instance.PRICE,
                 schema.dataset_model_instance.PRICE_USD, schema.dataset_model_instance.PRICE_PER_SQUARE_METER,
                 schema.dataset_model_instance.PRICE_USD_PER_SQUARE_METER),
        analysis_sql_files={
            "average_price_by_address": "datasets/house/select_average_price_by_address.sql",
            "average_price_per_square_meter_by_room": "datasets/house/select_average_price_per_square_meter_by_room.sql",
        },
    ),
    processors={
        "inmemory": InmemoryHouseProcessor(), "spark": SparkHouseProcessor()
    },

)
