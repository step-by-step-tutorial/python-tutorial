import dataset.house.model as schema
from app_config import env_config as ec
from dataset.definition import StageTable, Dataset, DataWarehouse, Datalake
from dataset.house.inmemory_processor import InmemoryHouseProcessor
from dataset.house.spark_processor import SparkHouseProcessor
from model.house_event import HouseEvent
from util.file_utils import read_text_file

HOUSE_DATASET = Dataset(
    name="house",
    file_name="house.csv",
    file_path=str(ec.ROOT / ec.RESOURCES_DIR / "house.csv"),
    dataframe_schema=schema.struct_type,
    required_columns=schema.required_columns,
    datalake=Datalake(bucket_name=ec.DATALAKE_BUCKET_NAME),
    database=StageTable(
        name="house_stage",
        columns=(schema.model.LISTING_KEY, schema.model.AREA,
                 schema.model.ROOM, schema.model.PARKING,
                 schema.model.WAREHOUSE, schema.model.ELEVATOR,
                 schema.model.ADDRESS, schema.model.PRICE,
                 schema.model.PRICE_USD, schema.model.PRICE_PER_SQUARE_METER,
                 schema.model.PRICE_USD_PER_SQUARE_METER),
        before_load_sql_files=("truncate_stage.sql",),
        after_load_sql_files=("upsert_listing.sql",),
    ),
    datawarehouse=DataWarehouse(
        table_name="house_table",
        full_table_name=f"{ec.DATAWAREHOUSE_NAME}.house_table",
        columns=schema.all_columns,
        preparing_sql_files={
            "truncate": read_text_file("truncate_datawarehouse.sql"),
        },
        analysis_sql_files={
            "revenue_by_category": read_text_file("select_revenue_by_category.sql"),
            "revenue_by_country": read_text_file("select_revenue_by_country.sql"),
        },
    ),
    processors={
        "inmemory": InmemoryHouseProcessor(), "spark": SparkHouseProcessor()
    },
    event_key_column=schema.model.ADDRESS_RAW,
    streaming_topic="house-events",
    streaming_consumer_group="house-spark-consumer",
    streaming_checkpoint_path=f"{ec.DATALAKE_SCHEME}://{ec.DATALAKE_BUCKET_NAME}/checkpoints/house-events",
    event_converter=lambda row: HouseEvent.from_dict(row).to_dict(),
)
