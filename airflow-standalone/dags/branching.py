import random
from datetime import datetime, timedelta

from airflow.decorators import dag
from airflow.operators.bash import BashOperator
from airflow.operators.python import BranchPythonOperator


def choose_path():
    random_choice = random.randint(1, 2)
    if random_choice == 1:
        return "path_1"
    else:
        return "path_2"


@dag(
    dag_id="branching",
    start_date=datetime.today(),
    schedule=timedelta(days=1)
)
def main_dag():
    start = BashOperator(
        task_id="start",
        bash_command="echo 'Start of the Branching DAG'"
    )

    branch = BranchPythonOperator(
        task_id='branch',
        python_callable=choose_path
    )

    path_1 = BashOperator(
        task_id="path_1",
        bash_command="echo 'Task on Path 1'"
    )

    path_2 = BashOperator(
        task_id="path_2",
        bash_command="echo 'Task on Path 2'"
    )

    end = BashOperator(
        task_id="end",
        bash_command="echo 'End of the Branching DAG'",
        trigger_rule="none_failed_min_one_success"
    )

    start >> branch
    branch >> [path_1, path_2]
    path_1 >> end
    path_2 >> end


dag = main_dag()
