from datetime import UTC, datetime
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG

DAG_ID = "spark_etl_dag"


def run_pipeline_method(method_name: str, **kwargs):
    from inspect import signature

    from config.settings import settings as main_settings
    from dataset.registry import get_dataset
    from pipeline.spark_pipeline import SparkPipeline

    pipeline = SparkPipeline(get_dataset(main_settings.app.dataset_name))
    method = getattr(pipeline, method_name)
    return method(**{name: value for name, value in kwargs.items() if name in signature(method).parameters})

with DAG(
        dag_id=DAG_ID,
        start_date=datetime(2026, 1, 1, tzinfo=UTC),
        schedule=None,
        catchup=False,
        tags={"spark", "etl", "datalake"}
) as dag:
    store_raw_data_task = PythonOperator(
        task_id="store_raw_data",
        python_callable=run_pipeline_method,
        op_args=("store_raw_data",),
    )

    clean_data_task = PythonOperator(
        task_id="clean_data",
        python_callable=run_pipeline_method,
        op_args=("cleaning",),
        op_kwargs={"raw_relative_path": store_raw_data_task.output}
    )

    enrich_data_task = PythonOperator(
        task_id="enrich_data",
        python_callable=run_pipeline_method,
        op_args=("enriching",),
        op_kwargs={"cleaned_relative_path": clean_data_task.output}
    )

    populate_database_task = PythonOperator(
        task_id="populate_database",
        python_callable=run_pipeline_method,
        op_args=("populate_database",),
        op_kwargs={"enriched_data_path": enrich_data_task.output}
    )

    populate_datawarehouse_task = PythonOperator(
        task_id="populate_datawarehouse",
        python_callable=run_pipeline_method,
        op_args=("populate_datawarehouse",),
        op_kwargs={"enriched_data_path": enrich_data_task.output}
    )

    show_dataframe_task = PythonOperator(
        task_id="show_dataframe",
        python_callable=run_pipeline_method,
        op_args=("show_dataframe",),
        op_kwargs={"enriched_data_path": enrich_data_task.output}
    )

    analyze_via_spark_task = PythonOperator(
        task_id="analyze_via_spark",
        python_callable=run_pipeline_method,
        op_args=("analyze_via_dataframe",),
        op_kwargs={"enriched_data_path": enrich_data_task.output}
    )

    analyze_via_datawarehouse_task = PythonOperator(
        task_id="analyze_via_datawarehouse",
        python_callable=run_pipeline_method,
        op_args=("analyzing_via_datawarehouse",),
    )

    store_raw_data_task >> clean_data_task >> enrich_data_task

    enrich_data_task >> [
        populate_database_task,
        populate_datawarehouse_task,
        show_dataframe_task,
        analyze_via_spark_task
    ]

    populate_datawarehouse_task >> analyze_via_datawarehouse_task
