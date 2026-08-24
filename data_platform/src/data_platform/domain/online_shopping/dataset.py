from data_platform.config.keys import Key
from data_platform.config.main_settings import settings as main_settings

from data_platform.domain.online_shopping.attribute import ONLINE_SHOPPING_ATTRIBUTE as columns
from data_platform.domain.online_shopping.inmemory_analyzer import InmemoryOnlineShoppingAnalyzer
from data_platform.domain.online_shopping.inmemory_transformer import InmemoryOnlineShoppingTransformer
from data_platform.ingestion.rest_api_csv_ingestor import RestApiCsvIngestor
from data_platform.model import (
    DataFrameModel,
    DataLakeEndpoint,
    DataWarehouseEndpoint,
    DatabaseEndpoint,
    Dataset,
    PipelineSteps,
    RestApiEndpoint,
)
from data_platform.persistence.data_lake_repository import DataLakeRepository
from data_platform.persistence.inmemory_database_repository import InmemoryDatabaseRepository
from data_platform.persistence.repository_data_exposer import RepositoryDataExposer
from data_platform.presentation.dataframe_display import show_map_of_dataframe
from data_platform.registry.endpoint_registry import audit_endpoint, endpoint_registry
from data_platform.service.dataframe_analysis_service import DataFrameAnalyzer

ONLINE_SHOPPING_DATASET = Dataset(
    name="online_shopping",
    dataframe=DataFrameModel(
        required_columns=frozenset(
            {
                columns.order_id,
                columns.order_date,
                columns.sales_channel,
                columns.country,
                columns.product_name,
                columns.unit_price,
                columns.quantity,
                columns.total_amount,
            }
        )
    ),
    audit=endpoint_registry.get_item(audit_endpoint.name),
    endpoints={
        Key.ONLINE_SHOPPING_REST_API: (
            RestApiEndpoint(
                name=Key.ONLINE_SHOPPING_REST_API,
                url=f"{main_settings.api["test_data"].url.rstrip('/')}/datasets/online_shopping/download?format=csv",
            )
        ),
        Key.ONLINE_SHOPPING_DATA_LAKE: (
            DataLakeEndpoint(
                name=Key.ONLINE_SHOPPING_DATA_LAKE,
                connection_name=Key.ONLINE_SHOPPING_DATA_LAKE,
                bucket_name=main_settings.data_lake[Key.PLATFORM_DATA_LAKE].bucket_name,
                scheme=main_settings.data_lake[Key.PLATFORM_DATA_LAKE].scheme,
            )
        ),
        Key.ONLINE_SHOPPING_DATABASE: (
            DatabaseEndpoint(
                name=Key.ONLINE_SHOPPING_DATABASE,
                connection_name=Key.ONLINE_SHOPPING_DATABASE,
                schema="online_shopping",
                stage_table_name="online_shopping_stage",
                full_stage_table_name="online_shopping.online_shopping_stage",
                table_names=["online_shopping.online_shopping_stage"],
                create_sql_files={
                    "create": "database/online_shopping/create_tables.sql"
                },
                truncate_sql_files={
                    "truncate": "database/online_shopping/truncate_stage.sql"
                },
                query_sql_files={"select_all": "database/select_all.sql"},
            )
        ),
        Key.ONLINE_SHOPPING_DATA_WAREHOUSE: (
            DataWarehouseEndpoint(
                name=Key.ONLINE_SHOPPING_DATA_WAREHOUSE,
                connection_name=Key.ONLINE_SHOPPING_DATA_WAREHOUSE,
                schema=main_settings.data_warehouse[
                    Key.ONLINE_SHOPPING_DATA_WAREHOUSE
                ].database_name,
                table_name="online_shopping_table",
                full_table_name=f"{main_settings.data_warehouse[Key.ONLINE_SHOPPING_DATA_WAREHOUSE].database_name}.online_shopping_table",
                create_sql_files={
                    "create_database": "datawarehouse/online_shopping/create_database.sql",
                    "create_table": "datawarehouse/online_shopping/create_table.sql",
                },
                truncate_sql_files={
                    "truncate": "datawarehouse/online_shopping/truncate_datawarehouse.sql"
                },
                query_sql_files={
                    "select_all": "datawarehouse/select_all.sql",
                    "revenue_by_country": "datawarehouse/online_shopping/select_revenue_by_country.sql",
                },
            )
        ),
    },
    pipeline_steps=PipelineSteps(
        storages=(),
        ingestors=(
            RestApiCsvIngestor(
                RestApiEndpoint(
                    name=Key.ONLINE_SHOPPING_REST_API,
                    url=f"{main_settings.api["test_data"].url.rstrip('/')}/datasets/online_shopping/download?format=csv",
                )
            ),
        ),
        cleaners=(InmemoryOnlineShoppingTransformer(),),
        enrichers=(InmemoryOnlineShoppingTransformer(),),
        exposers=(
            RepositoryDataExposer(
                DataLakeRepository(
                    DataLakeEndpoint(
                        name=Key.ONLINE_SHOPPING_DATA_LAKE,
                        connection_name=Key.ONLINE_SHOPPING_DATA_LAKE,
                        bucket_name=main_settings.data_lake[ Key.PLATFORM_DATA_LAKE].bucket_name,
                        scheme=main_settings.data_lake[Key.PLATFORM_DATA_LAKE].scheme,
                    )
                ).find,
                InmemoryDatabaseRepository(
                    DatabaseEndpoint(
                        name=Key.ONLINE_SHOPPING_DATABASE,
                        connection_name=Key.ONLINE_SHOPPING_DATABASE,
                        schema="online_shopping",
                        stage_table_name="online_shopping_stage",
                        full_stage_table_name="online_shopping.online_shopping_stage",
                        table_names=["online_shopping.online_shopping_stage"],
                        create_sql_files={
                            "create": "database/online_shopping/create_tables.sql"
                        },
                        truncate_sql_files={
                            "truncate": "database/online_shopping/truncate_stage.sql"
                        },
                        query_sql_files={"select_all": "database/select_all.sql"},
                    )
                ).replace,
            ),
        ),
        analyzers=(
            DataFrameAnalyzer(
                DataLakeRepository(
                    DataLakeEndpoint(
                        name=Key.ONLINE_SHOPPING_DATA_LAKE,
                        connection_name=Key.ONLINE_SHOPPING_DATA_LAKE,
                        bucket_name=main_settings.data_lake[Key.PLATFORM_DATA_LAKE].bucket_name,
                        scheme=main_settings.data_lake[Key.PLATFORM_DATA_LAKE].scheme,
                    )
                ).find,
                InmemoryOnlineShoppingAnalyzer(),
                show_map_of_dataframe,
            ),
        ),
    ),
)
