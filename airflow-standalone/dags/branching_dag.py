import random
from datetime import datetime, timedelta

from airflow.decorators import dag
from airflow.operators.bash import BashOperator
from airflow.operators.python import BranchPythonOperator


@dag(
    dag_id="branching_dag",
    start_date=datetime.today(),
    schedule=timedelta(days=1)
)
def branching_dag():
    start_task = BashOperator(
        task_id="start_task",
        bash_command="echo 'Start of the DAG'"
    )

    def choose_branch():
        random_choice = random.randint(1, 2)
        if random_choice == 1:
            return "path_1_task"
        else:
            return "path_2_task"

    branch_task = BranchPythonOperator(
        task_id='branch_task',
        python_callable=choose_branch
    )

    path_1_task = BashOperator(
        task_id="path_1_task",
        bash_command="echo 'Task on Path 1'"
    )

    path_2_task = BashOperator(
        task_id="path_2_task",
        bash_command="echo 'Task on Path 2'"
    )

    end_task = BashOperator(
        task_id="end_task",
        bash_command="echo 'End of the DAG'",
        trigger_rule="none_failed_min_one_success"  # Executes if at least one upstream task succeeded
    )

    start_task >> branch_task
    branch_task >> [path_1_task, path_2_task]
    path_1_task >> end_task
    path_2_task >> end_task


dag = branching_dag()
