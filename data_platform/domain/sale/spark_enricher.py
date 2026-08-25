from pyspark.sql import DataFrame
from pyspark.sql import functions as sf

from data_platform.domain.sale.attribute import SALE_ATTRIBUTE as schema


class SparkSaleEnricher:
    def enrich(self, dataframe: DataFrame) -> DataFrame:
        return (
            dataframe
            .withColumn(schema.total_price, sf.round(sf.col(schema.quantity) * sf.col(schema.unit_price), 2))
            .withColumn(schema.year, sf.year(schema.order_date))
            .withColumn(schema.month, sf.month(schema.order_date))
        )
