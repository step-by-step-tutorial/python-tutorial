from datetime import UTC, datetime
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG
from airflow.task.trigger_rule import TriggerRule

from data_platform.config.main_settings import settings as main_settings
from data_platform.registry.dataset_registry import dataset_registry
from data_platform.registry.bootstrap import initialize_registries
from data_platform.pipeline.spark_pipeline import SparkPipeline
from data_platform.adapter.dag_pipeline_adapter import DagPipelineAdapter

DAG_ID = "spark_etl_dag"

initialize_registries()
pipeline = SparkPipeline(dataset_registry.get_item(main_settings.app.dataset_name))
dag_pipeline_adapter = DagPipelineAdapter(pipeline)


with DAG(
        dag_id=DAG_ID,
        start_date=datetime(2026, 1, 1, tzinfo=UTC),
        schedule=None,
        catchup=False,
        tags={"spark", "etl", "datalake"}
) as dag:
    prepare_task = PythonOperator(
        task_id="prepare",
        python_callable=dag_pipeline_adapter.prepare,
    )

    ingest_raw_data_task = PythonOperator(
        task_id="ingest_raw_data",
        python_callable=dag_pipeline_adapter.ingest_raw_data,
    )

    clean_task = PythonOperator(
        task_id="clean",
        python_callable=dag_pipeline_adapter.clean,
        op_kwargs={"raw_relative_path": ingest_raw_data_task.output}
    )

    enrich_task = PythonOperator(
        task_id="enrich",
        python_callable=dag_pipeline_adapter.enrich,
        op_kwargs={"cleaned_relative_path": clean_task.output}
    )

    populate_enriched_data_task = PythonOperator(
        task_id="populate_enriched_data",
        python_callable=dag_pipeline_adapter.populate_enriched_data,
        op_kwargs={"enriched_data_path": enrich_task.output}
    )

    show_dataframe_task = PythonOperator(
        task_id="show_dataframe",
        python_callable=pipeline.show_dataframe,
        op_kwargs={"enriched_data_path": enrich_task.output}
    )

    analyze_enriched_data_task = PythonOperator(
        task_id="analyze_enriched_data",
        python_callable=dag_pipeline_adapter.analyze_enriched_data,
        op_kwargs={"enriched_data_path": enrich_task.output},
    )

    clean_up_task = PythonOperator(
        task_id="clean_up",
        python_callable=dag_pipeline_adapter.clean_up,
        trigger_rule=TriggerRule.ALL_DONE,
    )

    prepare_task >> ingest_raw_data_task >> clean_task >> enrich_task

    enrich_task >> [
        populate_enriched_data_task,
        show_dataframe_task,
        analyze_enriched_data_task
    ]

    populate_enriched_data_task >> analyze_enriched_data_task
    [populate_enriched_data_task, show_dataframe_task, analyze_enriched_data_task] >> clean_up_task
