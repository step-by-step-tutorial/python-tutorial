from time import sleep

import pendulum

from airflow import DAG
from airflow.decorators import task


def api_call():
    sleep(1000)
    return "Hello from Airflow!"


with DAG(
    dag_id="hello_python_operator",
    schedule=None,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    tags=["example"],
) as dag:

    @task()
    def print_api_response():
        response = api_call()
        print(response)