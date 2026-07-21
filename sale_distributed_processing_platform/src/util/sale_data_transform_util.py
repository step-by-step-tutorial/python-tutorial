from pyspark.sql import DataFrame
from pyspark.sql import functions as sf


def transform_sale_data(dataframe: DataFrame, ) -> DataFrame:
    return (
        dataframe
        .withColumn("total_price", sf.round(sf.col("quantity") * sf.col("unit_price"), 2))
        .withColumn("year", sf.year("order_date"))
        .withColumn("month", sf.month("order_date"))
    )
