from datetime import datetime, timedelta

from airflow.decorators import dag
from airflow.operators.bash import BashOperator


@dag(
    dag_id="bash_dependency",
    start_date=datetime.today(),
    schedule=timedelta(days=1),
)
def main_dag():
    start = BashOperator(
        task_id="start",
        bash_command="echo 'Start of dependency DAG'",
    )

    current_date = BashOperator(
        task_id="current_date",
        bash_command="date",
    )

    sleep = BashOperator(
        task_id="sleep",
        bash_command="sleep 5",
    )

    end = BashOperator(
        task_id="end",
        bash_command="echo 'End of dependency DAG'",
    )

    start >> current_date >> [sleep, end]


dag = main_dag()
