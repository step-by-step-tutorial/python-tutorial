from dataset.sale.columns import SaleColumns, sale_columns as model
from dataset.sale.spark_schema import build_schema

SALE_COLUMNS = model


required_columns = frozenset(
    {
        model.order_id,
        model.customer_name,
        model.product_name,
        model.category,
        model.quantity,
        model.unit_price,
        model.order_date,
        model.country,
    }
)

all_columns: tuple[str, ...] = (
    model.order_id,
    model.customer_name,
    model.product_name,
    model.category,
    model.quantity,
    model.unit_price,
    model.order_date,
    model.country,
    model.total_price,
    model.year,
    model.month,
    model.revenue,
)

def get_struct_type():
    return build_schema()
