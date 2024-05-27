import time

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago


def step_1():
    print("Step 1 executed")
    time.sleep(1)


def step_2():
    print("Step 1 executed")


def step_3():
    print("Step 1 executed")


def step_4():
    print("Step 1 executed")


def step_5():
    time.sleep(1)
    print("Step 1 executed")


with DAG(
        dag_id='hello_world_pipeline',
        description=" This the first dag include 5 steps",
        default_args={"owner": "airflow"},
        start_date=days_ago(1),
        schedule_interval="@once",
        tags=['hello_world_pipeline'],
        catchup=False,
) as dag:
    t1 = PythonOperator(task_id='step_1', python_callable=step_1)
    t2 = PythonOperator(task_id='step_2', python_callable=step_2)
    t3 = PythonOperator(task_id='step_3', python_callable=step_3)
    t4 = PythonOperator(task_id='step_4', python_callable=step_4)
    t5 = PythonOperator(task_id='step_5', python_callable=step_5)

t1 >> [t2, t3, t4] >> t5
