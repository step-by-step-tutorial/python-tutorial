from datetime import UTC, datetime

from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG

from config.app import settings as app_settings
from dataset.registry import get_dataset
from pipeline.spark_streaming_pipeline import SparkStreamingPipeline

DAG_ID = "spark_streaming_etl_dag"

pipeline = SparkStreamingPipeline(get_dataset(app_settings.dataset_name))

with DAG(
        dag_id=DAG_ID,
        start_date=datetime(2026, 1, 1, tzinfo=UTC),
        schedule=None,
        catchup=False,
        max_active_runs=1,
        tags={"spark", "streaming", "etl", "datalake"}
) as dag:
    publish_events_task = PythonOperator(
        task_id="publish_events",
        python_callable=pipeline.publish_events
    )

    process_stream_task = PythonOperator(
        task_id="process_stream",
        python_callable=pipeline.process_stream
    )

    populate_database_task = PythonOperator(
        task_id="populate_database",
        python_callable=pipeline.populate_database,
        op_kwargs={"enriched_data_path": process_stream_task.output}
    )

    populate_datawarehouse_task = PythonOperator(
        task_id="populate_datawarehouse",
        python_callable=pipeline.populate_datawarehouse,
        op_kwargs={"enriched_data_path": process_stream_task.output}
    )

    show_dataframe_task = PythonOperator(
        task_id="show_dataframe",
        python_callable=pipeline.show_dataframe,
        op_kwargs={"enriched_data_path": process_stream_task.output}
    )

    analyze_via_spark_task = PythonOperator(
        task_id="analyze_via_spark",
        python_callable=pipeline.analyzing_via_spark,
        op_kwargs={"enriched_data_path": process_stream_task.output}
    )

    analyze_via_datawarehouse_task = PythonOperator(
        task_id="analyze_via_datawarehouse",
        python_callable=pipeline.analyzing_via_datawarehouse
    )

    publish_events_task >> process_stream_task

    process_stream_task >> [
        populate_database_task,
        populate_datawarehouse_task,
        show_dataframe_task,
        analyze_via_spark_task
    ]

    populate_datawarehouse_task >> analyze_via_datawarehouse_task
