from airflow.decorators import task, dag
from airflow.utils.dates import days_ago


@dag(
    dag_id='hello_world_annotation',
    start_date=days_ago(1),
    schedule="0 0 * * *"
)
def hello_world_annotation():
    @task()
    def say_hello():
        print("hello world")


hello_world_annotation()
