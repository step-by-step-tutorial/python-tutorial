from datetime import datetime, timedelta

from airflow.decorators import dag
from airflow.operators.bash import BashOperator


@dag(
    dag_id="retry_timeout_task",
    start_date=datetime.today(),
    schedule=timedelta(days=1),
)
def retries_and_timeouts_dag():
    retry_task = BashOperator(
        task_id="retry_task",
        bash_command="exit 1",
        retries=3,
        retry_delay=timedelta(seconds=1)
    )

    timeout_task = BashOperator(
        task_id="timeout_task",
        bash_command="sleep 5",
        execution_timeout=timedelta(seconds=3),
        retries=0
    )

    retry_task >> timeout_task


dag = retries_and_timeouts_dag()
