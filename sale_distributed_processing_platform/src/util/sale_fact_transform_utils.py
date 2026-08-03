from pyspark.sql import DataFrame


def build_sale_warehouse_dataframe(dataframe: DataFrame, ) -> DataFrame:
    return dataframe.select(
        "order_id",
        "customer_name",
        "product_name",
        "category",
        "country",
        "quantity",
        "unit_price",
        "total_price",
        "order_date",
        "year",
        "month",
    )
