from pyspark.sql import DataFrame
from pyspark.sql import functions as sf


def clean_sale_data(dataframe: DataFrame) -> DataFrame:
    average_unit_price = (
        dataframe
        .select(sf.avg("unit_price").alias("average_unit_price"))
        .first()["average_unit_price"]
    )

    if average_unit_price is None:
        raise ValueError("Cannot clean sale data because unit_price has no valid values.")

    return (
        dataframe
        .withColumn("quantity", sf.coalesce(sf.col("quantity"), sf.lit(1.0)))
        .withColumn("unit_price", sf.coalesce(sf.col("unit_price"), sf.lit(float(average_unit_price))))
        .withColumn("order_date", sf.to_date(sf.col("order_date"), "yyyy-MM-dd", ))
        .dropna(subset=["order_date"])
    )
