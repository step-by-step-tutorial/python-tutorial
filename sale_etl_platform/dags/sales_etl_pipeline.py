from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.standard.operators.python import PythonOperator
from sales_etl_pipeline_service import SalesEtlPipelineService


def sales_etl_pipeline() -> None:
    sales_etl_pipeline_service = SalesEtlPipelineService()
    sales_etl_pipeline_service.run_pipeline()


with DAG(dag_id="sales_etl_pipeline") as dag:
    task1 = EmptyOperator(task_id="task_1")
    task2 = PythonOperator(task_id="sales_etl_pipeline", python_callable=sales_etl_pipeline)

    task1 >> task2
