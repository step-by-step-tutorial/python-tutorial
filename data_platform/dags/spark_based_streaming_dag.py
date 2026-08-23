from datetime import UTC, datetime

from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG

from data_platform.config.main_settings import settings as main_settings
from data_platform.registry.dataset_registry import dataset_registry
from data_platform.pipeline.spark_streaming_pipeline import SparkStreamingPipeline
from data_platform.adapter.dag_pipeline_adapter import DagPipelineAdapter

DAG_ID = "spark_streaming_etl_dag"

pipeline = SparkStreamingPipeline(dataset_registry.get_item(main_settings.app.dataset_name))
dag_pipeline_adapter = DagPipelineAdapter(pipeline)


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
        python_callable=dag_pipeline_adapter.ingest_raw_data,
    )

    clean_task = PythonOperator(
        task_id="clean",
        python_callable=dag_pipeline_adapter.clean,
        op_kwargs={"raw_relative_path": ingest_raw_data_task.output},
    )

    enrich_task = PythonOperator(
        task_id="enrich",
        python_callable=dag_pipeline_adapter.enrich,
        op_kwargs={"cleaned_relative_path": clean_task.output},
    )

    populate_database_task = PythonOperator(
        task_id="populate_database",
        python_callable=pipeline.populate_database,
        op_kwargs={"enriched_data_path": enrich_task.output},
    )

    populate_datawarehouse_task = PythonOperator(
        task_id="populate_datawarehouse",
        python_callable=pipeline.populate_datawarehouse,
        op_kwargs={"enriched_data_path": enrich_task.output},
    )

    show_dataframe_task = PythonOperator(
        task_id="show_dataframe",
        python_callable=pipeline.show_dataframe,
        op_kwargs={"enriched_data_path": enrich_task.output},
    )

    analyze_dataframe_task = PythonOperator(
        task_id="analyze_dataframe",
        python_callable=pipeline.analyze_dataframe,
        op_kwargs={"enriched_data_path": enrich_task.output},
    )

    analyze_via_datawarehouse_task = PythonOperator(
        task_id="analyze_via_datawarehouse",
        python_callable=pipeline.analyze_data_warehouse,
    )

    ingest_raw_data_task >> clean_task >> enrich_task
    enrich_task >> [
        populate_database_task,
        populate_datawarehouse_task,
        show_dataframe_task,
        analyze_dataframe_task,
    ]
    populate_datawarehouse_task >> analyze_via_datawarehouse_task
