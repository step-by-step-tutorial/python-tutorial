from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

with DAG(dag_id="hello_world_programmatic", start_date=days_ago(1), schedule="0 0 * * *") as dag:
    say_hello = BashOperator(task_id="hello", bash_command="echo hello world")

    say_hello
