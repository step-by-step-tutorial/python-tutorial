from datetime import UTC, datetime

from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG

from config.app import settings as app_settings
from dataset.registry import get_dataset
from pipeline.inmemory_pipeline import InmemoryPipeline

DAG_ID = "inmemory_etl_dag"

pipeline = InmemoryPipeline(get_dataset(app_settings.dataset_name))

with DAG(
        dag_id=DAG_ID,
        start_date=datetime(2026, 1, 1, tzinfo=UTC),
        schedule=None,
        catchup=False,
        tags={"inmemory", "etl", "datalake"},
) as dag:
    store_raw_data_task = PythonOperator(
        task_id="store_raw_data",
        python_callable=pipeline.store_raw_data,
    )

    clean_data_task = PythonOperator(
        task_id="clean_data",
        python_callable=pipeline.cleaning,
        op_kwargs={
            "raw_relative_path": store_raw_data_task.output,
        },
    )

    enrich_data_task = PythonOperator(
        task_id="enrich_data",
        python_callable=pipeline.enriching,
        op_kwargs={
            "cleaned_relative_path": clean_data_task.output,
        },
    )

    populate_database_task = PythonOperator(
        task_id="populate_database",
        python_callable=pipeline.populate_database,
        op_kwargs={
            "enriched_data_path": enrich_data_task.output,
        },
    )

    populate_datawarehouse_task = PythonOperator(
        task_id="populate_datawarehouse",
        python_callable=pipeline.populate_datawarehouse,
        op_kwargs={
            "enriched_data_path": enrich_data_task.output,
        },
    )

    show_dataframe_task = PythonOperator(
        task_id="show_dataframe",
        python_callable=pipeline.show_dataframe,
        op_kwargs={
            "enriched_data_path": enrich_data_task.output,
        },
    )

    analyze_via_memory_task = PythonOperator(
        task_id="analyze_via_memory",
        python_callable=pipeline.analyze_via_dataframe,
        op_kwargs={
            "enriched_data_path": enrich_data_task.output,
        },
    )

    analyze_via_datawarehouse_task = PythonOperator(
        task_id="analyze_via_datawarehouse",
        python_callable=pipeline.analyzing_via_datawarehouse,
    )

    store_raw_data_task >> clean_data_task >> enrich_data_task

    enrich_data_task >> [
        populate_database_task,
        populate_datawarehouse_task,
        show_dataframe_task,
        analyze_via_memory_task,
    ]

    populate_datawarehouse_task >> analyze_via_datawarehouse_task
