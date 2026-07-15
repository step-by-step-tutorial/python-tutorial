
from pyspark.sql import DataFrame
from pyspark.sql import functions as spark_functions


class SaleDataTransformationService:
    def transform_sale_data(
        self,
        cleaned_sale_dataframe: DataFrame,
    ) -> DataFrame:
        return (
            cleaned_sale_dataframe
            .withColumn(
                "total_price",
                spark_functions.round(
                    spark_functions.col("quantity")
                    * spark_functions.col("unit_price"),
                    2,
                ),
            )
            .withColumn("year", spark_functions.year("order_date"))
            .withColumn("month", spark_functions.month("order_date"))
        )

    def build_sale_warehouse_dataframe(
        self,
        transformed_sale_dataframe: DataFrame,
    ) -> DataFrame:
        return transformed_sale_dataframe.select(
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
