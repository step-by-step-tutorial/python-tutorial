from datetime import datetime, timedelta

from airflow.decorators import dag
from airflow.operators.bash import BashOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator


@dag(
    dag_id="parent_dag",
    start_date=datetime.today(),
    schedule=timedelta(days=1)
)
def parent_dag():
    start_task = BashOperator(
        task_id="start_task",
        bash_command="echo 'Parent DAG is running'"
    )

    trigger_child_dag = TriggerDagRunOperator(
        task_id="trigger_child_dag",
        trigger_dag_id="child_dag"
    )

    start_task >> trigger_child_dag


parent_dag_instance = parent_dag()
