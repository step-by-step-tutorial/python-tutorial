
from datetime import datetime

from airflow.providers.apache.spark.operators.spark_submit import (
    SparkSubmitOperator,
)
from airflow.sdk import DAG


with DAG(
    dag_id="sale_etl_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["sale", "spark", "batch", "data-engineering"],
) as dag:
    run_sale_etl_pipeline = SparkSubmitOperator(
        task_id="run_sale_etl_pipeline",
        application="/app/src/main.py",
        conn_id="spark_default",
        packages=",".join(
            [
                "org.postgresql:postgresql:42.7.7",
                "org.apache.hadoop:hadoop-aws:3.4.1",
                "software.amazon.awssdk:bundle:2.31.65",
            ]
        ),
        conf={
            "spark.executor.memory": "1g",
            "spark.executor.cores": "1",
            "spark.driver.memory": "1g",
        },
        env_vars={
            "PYTHONPATH": "/app",
            "SALE_APPLICATION_NAME": "sale-distributed-processing-platform",
            "SALE_SPARK_MASTER_URL": "spark://sale-spark-master:7077",
            "SALE_INPUT_CSV_PATH": "/app/data/sale.csv",
            "SALE_POSTGRES_JDBC_URL": (
                "jdbc:postgresql://sale-postgres:5432/sale_oltp"
            ),
            "SALE_POSTGRES_HOST": "sale-postgres",
            "SALE_POSTGRES_PORT": "5432",
            "SALE_POSTGRES_DATABASE": "sale_oltp",
            "SALE_POSTGRES_USER": "sale_platform_user",
            "SALE_POSTGRES_PASSWORD": "sale_platform_password",
            "SALE_DATA_LAKE_ENDPOINT": "http://sale-data-lake:9000",
            "SALE_DATA_LAKE_ACCESS_KEY": "sale_data_lake_user",
            "SALE_DATA_LAKE_SECRET_KEY": "sale_data_lake_password",
            "SALE_DATA_LAKE_BUCKET": "sale-data-lake",
            "SALE_CURATED_OUTPUT_PATH": "curated/sale",
            "SALE_WAREHOUSE_HOST": "sale-warehouse",
            "SALE_WAREHOUSE_HTTP_PORT": "8123",
            "SALE_WAREHOUSE_DATABASE": "sale_warehouse",
            "SALE_WAREHOUSE_USER": "sale_warehouse_user",
            "SALE_WAREHOUSE_PASSWORD": "sale_warehouse_password",
        },
        verbose=True,
    )
