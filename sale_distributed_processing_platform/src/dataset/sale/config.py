from app_config import env_config as ec
from dataset.definition import StageTable, Dataset, DataWarehouse, Datalake
from dataset.sale.inmemory_processor import InmemorySaleProcessor
import dataset.sale.schema as schema
from dataset.sale.spark_processor import SparkSaleProcessor

SALE_DATASET = Dataset(
    name="Sale",
    file_name="sale.csv",
    dataframe_schema=schema.DATAFRAME_SCHEMA,
    required_columns=schema.REQUIRED_COLUMNS,
    event_key_column=schema.dataset_model_instance.ORDER_ID,
    streaming_topic="sale-events",
    streaming_consumer_group="sale-spark-consumer",
    datalake=Datalake(bucket_name=ec.DATALAKE_BUCKET_NAME),
    streaming_checkpoint_path=f"{ec.DATALAKE_SCHEME}://{ec.DATALAKE_BUCKET_NAME}/checkpoints/sale-events",
    database=StageTable(
        name="sale_stage",
        columns=schema.ALL_COLUMNS,
        before_load_sql_files=("datasets/sale/truncate_stage.sql",),
        after_load_sql_files=(
            "datasets/sale/upsert_customer.sql", "datasets/sale/upsert_product.sql",
            "datasets/sale/upsert_order.sql", "datasets/sale/upsert_order_item.sql")
        ,
    ),
    datawarehouse=DataWarehouse(
        table_name="sale_table",
        columns=schema.ALL_COLUMNS,
        analysis_sql_files={
            "revenue_by_category": "datasets/sale/select_revenue_by_category.sql",
            "revenue_by_country": "datasets/sale/select_revenue_by_country.sql",
        },
    ),
    processors={
        "inmemory": InmemorySaleProcessor(), "spark": SparkSaleProcessor()
    },
)
