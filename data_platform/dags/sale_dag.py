from datetime import UTC, datetime

from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG
from airflow.task.trigger_rule import TriggerRule

from data_platform.adapter.dag_pipeline_adapter import DagPipelineAdapter
from data_platform.domain.sale.dataset import SALE_DATASET
from data_platform.pipeline.configured_pipeline import ConfiguredPipeline
from data_platform.registry.bootstrap import initialize_registries

initialize_registries()
pipeline = ConfiguredPipeline(SALE_DATASET)
adapter = DagPipelineAdapter(pipeline)

with DAG(dag_id="sale", start_date=datetime(2026, 1, 1, tzinfo=UTC), schedule=None, catchup=False, tags={"sale", "etl", "datalake"}) as dag:
    prepare = PythonOperator(task_id="prepare", python_callable=adapter.prepare)
    ingest = PythonOperator(task_id="ingest", python_callable=adapter.ingest)
    clean = PythonOperator(task_id="clean", python_callable=adapter.clean, op_kwargs={"raw_artifact_paths": ingest.output})
    enrich = PythonOperator(task_id="enrich", python_callable=adapter.enrich, op_kwargs={"cleaned_artifact_paths": clean.output})
    expose = PythonOperator(task_id="expose", python_callable=adapter.expose, op_kwargs={"enriched_artifact_paths": enrich.output})
    analyze = PythonOperator(task_id="analyze", python_callable=adapter.analyze, op_kwargs={"enriched_artifact_paths": enrich.output})
    cleanup = PythonOperator(task_id="cleanup", python_callable=adapter.cleanup, trigger_rule=TriggerRule.ALL_DONE)

    prepare >> ingest >> clean >> enrich >> expose >> analyze >> cleanup


