from datetime import UTC, datetime

from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG
from airflow.task.trigger_rule import TriggerRule

from data_platform.adapter.dag_pipeline_adapter import DagPipelineAdapter
from data_platform.domain.online_shopping.dataset import ONLINE_SHOPPING_DATASET
from data_platform.pipeline.online_shopping_inmemory_pipeline import OnlineShoppingInmemoryPipeline
from data_platform.registry.bootstrap import initialize_registries

DAG_ID = "online_shopping_inmemory_etl_dag"

initialize_registries()
dag_pipeline_adapter = DagPipelineAdapter(OnlineShoppingInmemoryPipeline(ONLINE_SHOPPING_DATASET))

with DAG(
    dag_id=DAG_ID,
    start_date=datetime(2026, 1, 1, tzinfo=UTC),
    schedule=None,
    catchup=False,
    tags={"inmemory", "etl", "online-shopping", "test-data-api"},
) as dag:
    prepare_task = PythonOperator(task_id="prepare", python_callable=dag_pipeline_adapter.prepare)
    ingest_raw_data_task = PythonOperator(task_id="ingest_raw_data", python_callable=dag_pipeline_adapter.ingest_raw_data)
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
    show_dataframe_task = PythonOperator(
        task_id="show_dataframe",
        python_callable=dag_pipeline_adapter.show_dataframe,
        op_kwargs={"enriched_data_path": enrich_task.output},
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
    enrich_task >> show_dataframe_task
    enrich_task >> analyze_enriched_data_task
    show_dataframe_task >> clean_up_task
    analyze_enriched_data_task >> clean_up_task
