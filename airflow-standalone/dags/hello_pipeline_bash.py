from datetime import datetime, timedelta

from airflow.decorators import dag
from airflow.operators.bash import BashOperator


@dag(
    dag_id="hello_pipeline_bash_operator",
    start_date=datetime.today(),
    schedule=timedelta(days=1),
)
def hello_pipeline():
    start = BashOperator(
        task_id="start",
        bash_command="echo Start of pipeline",
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
        bash_command="echo End of pipeline",
    )

    start >> current_date >> [sleep, end]


dag = hello_pipeline()
