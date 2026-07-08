import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.empty import EmptyOperator

with DAG(dag_id="hello_world") as dag:
    task1 = EmptyOperator(task_id="task")

    task1
