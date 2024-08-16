import time
from datetime import datetime, timedelta

from airflow.decorators import dag, task


@dag(
    dag_id="hello_pipeline_python_operator",
    start_date=datetime.today(),
    schedule=timedelta(days=1),
)
def hello_pipeline():
    @task
    def start():
        print("Start of pipeline")

    @task
    def current_date():
        print(f"Current date: {datetime.now()}")

    @task
    def sleep():
        time.sleep(5)
        return "Done sleeping..."

    @task
    def end():
        print("End of pipeline")

    start() >> current_date() >> [sleep(), end()]


dag = hello_pipeline()
