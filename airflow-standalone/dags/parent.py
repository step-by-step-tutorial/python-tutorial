from datetime import datetime, timedelta

from airflow.decorators import dag
from airflow.operators.bash import BashOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator


@dag(
    dag_id="parent",
    start_date=datetime.today(),
    schedule=timedelta(days=1)
)
def main_dag():
    start = BashOperator(
        task_id="start",
        bash_command="echo 'Parent DAG is running'"
    )

    trigger = TriggerDagRunOperator(
        task_id="trigger",
        trigger_dag_id="child"
    )

    start >> trigger


dag = main_dag()
