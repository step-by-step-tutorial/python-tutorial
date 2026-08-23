from datetime import UTC, datetime

from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG

from config.settings import settings as main_settings
from dataset.registry import get_dataset
from pipeline.spark_streaming_pipeline import SparkStreamingPipeline

DAG_ID = "spark_streaming_etl_dag"

pipeline = SparkStreamingPipeline(get_dataset(main_settings.app.dataset_name))


def ingest_raw_data() -> str:
    return pipeline.store_raw_data(pipeline.ingest_raw_data())


def cleaning(raw_relative_path: str) -> str:
    return pipeline.store_cleaned_data(pipeline.cleaning(raw_relative_path))


def enriching(cleaned_relative_path: str) -> str:
    return pipeline.store_enriched_data(pipeline.enriching(cleaned_relative_path))


with DAG(
        dag_id=DAG_ID,
        start_date=datetime(2026, 1, 1, tzinfo=UTC),
        schedule=None,
        catchup=False,
        max_active_runs=1,
        tags={"spark", "streaming", "etl", "datalake"},
) as dag:
    ingest_raw_data_task = PythonOperator(
        task_id="ingest_raw_data",
        python_callable=ingest_raw_data,
    )

    cleaning_task = PythonOperator(
        task_id="cleaning",
        python_callable=cleaning,
        op_kwargs={"raw_relative_path": ingest_raw_data_task.output},
    )

    enriching_task = PythonOperator(
        task_id="enriching",
        python_callable=enriching,
        op_kwargs={"cleaned_relative_path": cleaning_task.output},
    )

    populate_database_task = PythonOperator(
        task_id="populate_database",
        python_callable=pipeline.populate_database,
        op_kwargs={"enriched_data_path": enriching_task.output},
    )

    populate_datawarehouse_task = PythonOperator(
        task_id="populate_datawarehouse",
        python_callable=pipeline.populate_datawarehouse,
        op_kwargs={"enriched_data_path": enriching_task.output},
    )

    show_dataframe_task = PythonOperator(
        task_id="show_dataframe",
        python_callable=pipeline.show_dataframe,
        op_kwargs={"enriched_data_path": enriching_task.output},
    )

    analyze_via_dataframe_task = PythonOperator(
        task_id="analyze_via_dataframe",
        python_callable=pipeline.analyze_via_dataframe,
        op_kwargs={"enriched_data_path": enriching_task.output},
    )

    analyze_via_datawarehouse_task = PythonOperator(
        task_id="analyze_via_datawarehouse",
        python_callable=pipeline.analyzing_via_datawarehouse,
    )

    ingest_raw_data_task >> cleaning_task >> enriching_task
    enriching_task >> [
        populate_database_task,
        populate_datawarehouse_task,
        show_dataframe_task,
        analyze_via_dataframe_task,
    ]
    populate_datawarehouse_task >> analyze_via_datawarehouse_task
