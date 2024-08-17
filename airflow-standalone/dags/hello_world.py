from datetime import datetime, timedelta

from airflow.decorators import dag
from airflow.operators.bash import BashOperator


@dag(
    dag_id="hello_world",
    start_date=datetime.today(),
    schedule=timedelta(days=1),
)
def main_dag():
    task = BashOperator(
        task_id="task",
        bash_command="echo 'Hello World!'"
    )

    task


dag = main_dag()
