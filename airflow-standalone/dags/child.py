from datetime import datetime, timedelta

from airflow.decorators import dag
from airflow.operators.bash import BashOperator


@dag(
    dag_id="child",
    start_date=datetime.today(),
    schedule=timedelta(days=1),
)
def main_dag():
    task = BashOperator(
        task_id="task",
        bash_command="echo 'Child DAG is running'"
    )

    task


dag = main_dag()
