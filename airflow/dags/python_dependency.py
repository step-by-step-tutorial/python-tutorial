import time
from datetime import datetime, timedelta

from airflow.decorators import dag, task


@dag(
    dag_id="python_dependency",
    start_date=datetime.today(),
    schedule=timedelta(days=1),
)
def main_dag():
    @task
    def start():
        print("Start of dependency DAG")

    @task
    def current_date():
        print(f"Current date: {datetime.now()}")

    @task
    def sleep():
        time.sleep(5)
        print("Done sleeping...")

    @task
    def end():
        print("End of dependency DAG")

    start() >> current_date() >> [sleep(), end()]


dag = main_dag()
