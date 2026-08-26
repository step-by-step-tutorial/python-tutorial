from pyspark.sql.types import DoubleType, IntegerType, StringType, StructField, StructType, TimestampType

from data_platform.domain.online_shopping.attribute import attribute

_INTEGER_COLUMNS = {attribute.customer_id, attribute.quantity, attribute.delivery_days, attribute.year, attribute.month}
_DOUBLE_COLUMNS = {attribute.unit_price, attribute.subtotal, attribute.discount_percent, attribute.shipping_cost,
                   attribute.tax_amount, attribute.total_amount, attribute.discount_amount, attribute.net_revenue,
                   attribute.revenue}
_TIMESTAMP_COLUMNS = {attribute.order_date, attribute.estimated_delivery_date}
_DERIVED_COLUMNS = {attribute.discount_amount, attribute.net_revenue, attribute.year, attribute.month,
                    attribute.revenue}

ONLINE_SHOPPING_SCHEMA = StructType([
    *[
        StructField(column,
                    IntegerType() if column in _INTEGER_COLUMNS else DoubleType() if column in _DOUBLE_COLUMNS else TimestampType() if column in _TIMESTAMP_COLUMNS else StringType(),
                    nullable=True)
        for column in attribute.__dataclass_fields__ if column not in _DERIVED_COLUMNS
    ],
    StructField(attribute.discount_amount, DoubleType(), nullable=True),
    StructField(attribute.net_revenue, DoubleType(), nullable=True),
    StructField(attribute.year, IntegerType(), nullable=True),
    StructField(attribute.month, IntegerType(), nullable=True),
    StructField(attribute.revenue, DoubleType(), nullable=True),
])
