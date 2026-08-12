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


model = DatasetModel()

required_columns = frozenset[str](
    {
        model.ORDER_ID,
        model.CUSTOMER_NAME,
        model.PRODUCT_NAME,
        model.CATEGORY,
        model.QUANTITY,
        model.UNIT_PRICE,
        model.ORDER_DATE,
        model.COUNTRY
    }
)

all_columns: tuple[str, ...] = (
    model.ORDER_ID,
    model.CUSTOMER_NAME,
    model.PRODUCT_NAME,
    model.CATEGORY,
    model.QUANTITY,
    model.UNIT_PRICE,
    model.ORDER_DATE,
    model.COUNTRY,
    model.TOTAL_PRICE,
    model.YEAR,
    model.MONTH,
    model.REVENUE
)

struct_type = StructType(
    [
        StructField(model.ORDER_ID, LongType(), nullable=False),
        StructField(model.CUSTOMER_NAME, StringType(), nullable=False),
        StructField(model.PRODUCT_NAME, StringType(), nullable=False),
        StructField(model.CATEGORY, StringType(), nullable=False),
        StructField(model.QUANTITY, DoubleType(), nullable=True),
        StructField(model.UNIT_PRICE, DoubleType(), nullable=True),
        StructField(model.ORDER_DATE, StringType(), nullable=True),
        StructField(model.COUNTRY, StringType(), nullable=False),
    ]
)
