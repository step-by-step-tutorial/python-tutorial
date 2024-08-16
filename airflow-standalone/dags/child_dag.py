from datetime import datetime, timedelta

from airflow.decorators import dag
from airflow.operators.bash import BashOperator


@dag(
    dag_id="child_dag",
    start_date=datetime.today(),
    schedule=timedelta(days=1),
)
def child_dag():
    run_task = BashOperator(
        task_id="run_task",
        bash_command="echo 'Child DAG is running'"
    )

    run_task


child_dag_instance = child_dag()
