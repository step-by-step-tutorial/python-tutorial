from datetime import datetime, timedelta

from airflow.decorators import dag
from airflow.operators.bash import BashOperator


@dag(
    dag_id="parallel_tasks_dag",
    start_date=datetime.today(),
    schedule=timedelta(days=1)
)
def parallel_tasks_dag():
    task_1 = BashOperator(
        task_id="task_1",
        bash_command="echo 'This is Task 1'"
    )

    task_2 = BashOperator(
        task_id="task_2",
        bash_command="echo 'This is Task 2'"
    )

    task_3 = BashOperator(
        task_id="task_3",
        bash_command="echo 'This is Task 3'"
    )

    final_task = BashOperator(
        task_id="final_task",
        bash_command="echo 'All tasks are complete!'"
    )

    [task_1, task_2, task_3] >> final_task


dag = parallel_tasks_dag()
