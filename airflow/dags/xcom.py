from datetime import datetime, timedelta

from airflow.decorators import dag, task


@dag(
    dag_id="xcom",
    start_date=datetime.today(),
    schedule=timedelta(days=1),
)
def main_dag():
    @task
    def push_to_xcom():
        return "Hello from Task 1!"

    @task
    def pull_from_xcom(string):
        print(f"Task 2 received the value: {string}")

    value = push_to_xcom()
    pull_from_xcom(value)


dag = main_dag()
