from datetime import datetime, timedelta

from airflow.decorators import dag
from airflow.operators.bash import BashOperator


@dag(
    dag_id="retry_timeout",
    start_date=datetime.today(),
    schedule=timedelta(days=1),
)
def retries_and_timeouts_dag():
    start = BashOperator(
        task_id="start",
        bash_command="echo 'Start of retry_timeout DAG'",
    )

    retry = BashOperator(
        task_id="retry",
        bash_command="exit 1",
        retries=3,
        retry_delay=timedelta(seconds=1)
    )

    timeout = BashOperator(
        task_id="timeout",
        bash_command="sleep 5",
        execution_timeout=timedelta(seconds=3),
        retries=0
    )

    start >> [retry, timeout]


dag = retries_and_timeouts_dag()
