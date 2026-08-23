from data_platform.config.main_settings import settings as main_settings
from data_platform.keys import Key
from data_platform.model import (
    DataLakeEndpoint,
    DataWarehouseEndpoint,
    DataFrameDefinition,
    DatabaseEndpoint,
    Dataset,
    FileEndpoint,
    MessagingEndpoint,
    RestApiEndpoint,
)
from data_platform.model.sale_attribute import SALE_ATTRIBUTE
from data_platform.dataset.endpoint_registry import endpoint_registry
from data_platform.dataset.shared_endpoints import AUDIT_ENDPOINT
from data_platform.dataset.sale_spark_schema import build_schema
from data_platform.processor.inmemory_sale_processor import InmemorySaleProcessor
from data_platform.processor.spark_sale_processor import SparkSaleProcessor

SALE_DATASET = Dataset(
    name="Sale",
    dataframe=DataFrameDefinition(
        schema=build_schema(),
        required_columns=frozenset(
            {
                SALE_ATTRIBUTE.order_id,
                SALE_ATTRIBUTE.customer_name,
                SALE_ATTRIBUTE.product_name,
                SALE_ATTRIBUTE.category,
                SALE_ATTRIBUTE.quantity,
                SALE_ATTRIBUTE.unit_price,
                SALE_ATTRIBUTE.order_date,
                SALE_ATTRIBUTE.country,
            }
        ),
    ),
    audit=endpoint_registry.get(AUDIT_ENDPOINT.name),
    endpoints={
        Key.SALE_FILE_CSV: FileEndpoint(
            name=Key.SALE_FILE_CSV,
            file_name="sale.csv",
            file_path=str(main_settings.app.root / main_settings.app.resources_dir / "sale.csv"),
        ),
        Key.SALE_REST: RestApiEndpoint(
            name=Key.SALE_REST,
            url=main_settings.test_data.download_url,
        ),
        Key.SALE_KAFKA_LISTENER: MessagingEndpoint(
            name=Key.SALE_KAFKA_LISTENER,
            connection_name=Key.SALE_KAFKA_LISTENER,
            channel_name=main_settings.messaging[Key.SALE_KAFKA_LISTENER].channel_name,
            bootstrap_servers=main_settings.messaging[Key.SALE_KAFKA_LISTENER].bootstrap_servers,
            starting_offsets=main_settings.messaging[Key.SALE_KAFKA_LISTENER].starting_offsets,
        ),
        Key.SALE_KAFKA_PRODUCER: MessagingEndpoint(
            name=Key.SALE_KAFKA_PRODUCER,
            connection_name=Key.SALE_KAFKA_PRODUCER,
            channel_name=main_settings.messaging[Key.SALE_KAFKA_PRODUCER].channel_name,
            bootstrap_servers=main_settings.messaging[Key.SALE_KAFKA_PRODUCER].bootstrap_servers,
        ),
        Key.SALE_DATALAKE: DataLakeEndpoint(
            name=Key.SALE_DATALAKE,
            connection_name=Key.SALE_DATALAKE,
            bucket_name=main_settings.data_lake[Key.SALE_DATALAKE].bucket_name,
            scheme=main_settings.data_lake[Key.SALE_DATALAKE].scheme,
        ),
        Key.SALE_DATABASE: DatabaseEndpoint(
            name=Key.SALE_DATABASE,
            connection_name=Key.SALE_DATABASE,
            schema="sale",
            stage_table_name="sale_stage",
            full_stage_table_name="sale.sale_stage",
            table_names=[
                "sale.sale_stage",
                "sale.customer",
                "sale.product",
                "sale.order",
                "sale.order_item",
            ],
            create_sql_files={"create": "database/sale/create_tables.sql"},
            truncate_sql_files={"truncate": "database/sale/truncate_stage.sql"},
            write_sql_files={
                "customer": "database/sale/upsert_customer.sql",
                "product": "database/sale/upsert_product.sql",
                "order": "database/sale/upsert_order.sql",
                "order_item": "database/sale/upsert_order_item.sql",
            },
            query_sql_files={"select_all": "database/select_all.sql"},
        ),
        Key.SALE_DATAWAREHOUSE: DataWarehouseEndpoint(
            name=Key.SALE_DATAWAREHOUSE,
            connection_name=Key.SALE_DATAWAREHOUSE,
            schema=main_settings.data_warehouse[Key.SALE_DATAWAREHOUSE].database_name,
            table_name="sale_table",
            full_table_name=f"{main_settings.data_warehouse[Key.SALE_DATAWAREHOUSE].database_name}.sale_table",
            create_sql_files={
                "create_database": "datawarehouse/sale/create_database.sql",
                "create_table": "datawarehouse/sale/create_table.sql",
            },
            truncate_sql_files={
                "truncate": "datawarehouse/sale/truncate_datawarehouse.sql"
            },
            write_sql_files={},
            query_sql_files={
                "select_all": "datawarehouse/select_all.sql",
                "revenue_by_category": "datawarehouse/sale/select_revenue_by_category.sql",
                "revenue_by_country": "datawarehouse/sale/select_revenue_by_country.sql",
            },
        ),
    },
    processors={
        "inmemory": InmemorySaleProcessor(),
        "spark": SparkSaleProcessor(),
    },
)
