from datetime import datetime, timedelta

from airflow.decorators import dag, task


@dag(
    dag_id="xcom_dag",
    start_date=datetime.today(),
    schedule=timedelta(days=1),
)
def xcom_example_dag():
    @task
    def push_to_xcom():
        message = "Hello from Task 1!"
        return message

    @task
    def pull_from_xcom(message):
        print(f"Task 2 received the message: {message}")

    message = push_to_xcom()
    pull_from_xcom(message)


dag = xcom_example_dag()
