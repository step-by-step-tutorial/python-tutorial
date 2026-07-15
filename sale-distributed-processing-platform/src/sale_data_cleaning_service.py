
from pyspark.sql import DataFrame
from pyspark.sql import functions as spark_functions


class SaleDataCleaningService:
    def clean_sale_data(
        self,
        sale_dataframe: DataFrame,
    ) -> DataFrame:
        average_unit_price = (
            sale_dataframe
            .select(
                spark_functions.avg("unit_price").alias(
                    "average_unit_price"
                )
            )
            .first()["average_unit_price"]
        )

        if average_unit_price is None:
            raise ValueError(
                "Cannot clean sale data because unit_price has no valid values."
            )

        return (
            sale_dataframe
            .withColumn(
                "quantity",
                spark_functions.coalesce(
                    spark_functions.col("quantity"),
                    spark_functions.lit(1.0),
                ),
            )
            .withColumn(
                "unit_price",
                spark_functions.coalesce(
                    spark_functions.col("unit_price"),
                    spark_functions.lit(float(average_unit_price)),
                ),
            )
            .withColumn(
                "order_date",
                spark_functions.to_date(
                    spark_functions.col("order_date"),
                    "yyyy-MM-dd",
                ),
            )
            .dropna(subset=["order_date"])
        )
