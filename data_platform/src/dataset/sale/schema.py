from dataclasses import dataclass

from pyspark.sql.types import DoubleType, LongType, StringType, StructField, StructType


@dataclass(frozen=True)
class DatasetModel:
    ORDER_ID: str = "order_id"
    CUSTOMER_NAME: str = "customer_name"
    PRODUCT_NAME: str = "product_name"
    CATEGORY: str = "category"
    QUANTITY: str = "quantity"
    UNIT_PRICE: str = "unit_price"
    ORDER_DATE: str = "order_date"
    COUNTRY: str = "country"
    TOTAL_PRICE: str = "total_price"
    YEAR: str = "year"
    MONTH: str = "month"
    REVENUE: str = "revenue"


dataset_model_instance = DatasetModel()

REQUIRED_COLUMNS = frozenset[str](
    {
        dataset_model_instance.ORDER_ID,
        dataset_model_instance.CUSTOMER_NAME,
        dataset_model_instance.PRODUCT_NAME,
        dataset_model_instance.CATEGORY,
        dataset_model_instance.QUANTITY,
        dataset_model_instance.UNIT_PRICE,
        dataset_model_instance.ORDER_DATE,
        dataset_model_instance.COUNTRY
    }
)

ALL_COLUMNS: tuple[str, ...] = (
    dataset_model_instance.ORDER_ID,
    dataset_model_instance.CUSTOMER_NAME,
    dataset_model_instance.PRODUCT_NAME,
    dataset_model_instance.CATEGORY,
    dataset_model_instance.QUANTITY,
    dataset_model_instance.UNIT_PRICE,
    dataset_model_instance.ORDER_DATE,
    dataset_model_instance.COUNTRY,
    dataset_model_instance.TOTAL_PRICE,
    dataset_model_instance.YEAR,
    dataset_model_instance.MONTH,
    dataset_model_instance.REVENUE
)

DATAFRAME_SCHEMA = StructType(
    [
        StructField(dataset_model_instance.ORDER_ID, LongType(), nullable=False),
        StructField(dataset_model_instance.CUSTOMER_NAME, StringType(), nullable=False),
        StructField(dataset_model_instance.PRODUCT_NAME, StringType(), nullable=False),
        StructField(dataset_model_instance.CATEGORY, StringType(), nullable=False),
        StructField(dataset_model_instance.QUANTITY, DoubleType(), nullable=True),
        StructField(dataset_model_instance.UNIT_PRICE, DoubleType(), nullable=True),
        StructField(dataset_model_instance.ORDER_DATE, StringType(), nullable=True),
        StructField(dataset_model_instance.COUNTRY, StringType(), nullable=False),
    ]
)
