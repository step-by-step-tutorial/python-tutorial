from data_platform.config.keys import Key
from data_platform.config.main_settings import settings as main_settings
from data_platform.domain.online_shopping.attribute import ONLINE_SHOPPING_ATTRIBUTE as columns
from data_platform.domain.online_shopping.inmemory_analyzer import InmemoryOnlineShoppingAnalyzer
from data_platform.domain.online_shopping.inmemory_transformer import InmemoryOnlineShoppingTransformer
from data_platform.model import DataFrameModel, DataLakeEndpoint, Dataset, RestApiEndpoint
from data_platform.registry.dataset_registry import dataset_registry
from data_platform.registry.endpoint_registry import audit_endpoint, endpoint_registry

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
        Key.ONLINE_SHOPPING_REST_API: RestApiEndpoint(
            name=Key.ONLINE_SHOPPING_REST_API,
            url=f"{main_settings.test_data.api_url.rstrip('/')}/datasets/online_shopping/download?format=csv",
        ),
        Key.ONLINE_SHOPPING_DATA_LAKE: DataLakeEndpoint(
            name=Key.ONLINE_SHOPPING_DATA_LAKE,
            connection_name=Key.ONLINE_SHOPPING_DATA_LAKE,
            bucket_name=main_settings.data_lake[Key.PLATFORM_DATA_LAKE].bucket_name,
            scheme=main_settings.data_lake[Key.PLATFORM_DATA_LAKE].scheme,
        ),
    },
    transformers={"inmemory": InmemoryOnlineShoppingTransformer()},
    analyzers={"inmemory": InmemoryOnlineShoppingAnalyzer()},
)


def register_online_shopping_dataset() -> None:
    if not dataset_registry.contains(ONLINE_SHOPPING_DATASET.name):
        dataset_registry.register(ONLINE_SHOPPING_DATASET.name, ONLINE_SHOPPING_DATASET)
