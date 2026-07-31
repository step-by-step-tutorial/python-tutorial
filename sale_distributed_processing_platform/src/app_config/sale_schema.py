from dataclasses import dataclass

from pyspark.sql.types import DoubleType, IntegerType, StringType, StructField, StructType


@dataclass(frozen=True)
class SaleColumns:
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


SALE_COLUMNS = SaleColumns()

SALE_REQUIRED_COLUMNS = {
    SALE_COLUMNS.ORDER_ID,
    SALE_COLUMNS.CUSTOMER_NAME,
    SALE_COLUMNS.PRODUCT_NAME,
    SALE_COLUMNS.CATEGORY,
    SALE_COLUMNS.QUANTITY,
    SALE_COLUMNS.UNIT_PRICE,
    SALE_COLUMNS.ORDER_DATE,
    SALE_COLUMNS.COUNTRY,
}

SCHEMA = StructType(
    [
        StructField(SALE_COLUMNS.ORDER_ID, IntegerType(), nullable=False),
        StructField(SALE_COLUMNS.CUSTOMER_NAME, StringType(), nullable=False),
        StructField(SALE_COLUMNS.PRODUCT_NAME, StringType(), nullable=False),
        StructField(SALE_COLUMNS.CATEGORY, StringType(), nullable=False),
        StructField(SALE_COLUMNS.QUANTITY, DoubleType(), nullable=True),
        StructField(SALE_COLUMNS.UNIT_PRICE, DoubleType(), nullable=True),
        StructField(SALE_COLUMNS.ORDER_DATE, StringType(), nullable=True),
        StructField(SALE_COLUMNS.COUNTRY, StringType(), nullable=False),
    ]
)
