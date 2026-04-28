from datetime import datetime, timedelta

from airflow.decorators import dag
from airflow.operators.bash import BashOperator
from airflow.operators.email import EmailOperator
from airflow.utils.email import send_email


def failure_email(context):
    subject = f"Task Failed: {context['task_instance_key_str']}"
    body = f"""
        Task failed: {context['task_instance_key_str']}
        Dag: {context['dag'].dag_id}
        Task: {context['task'].task_id}
        Execution Time: {context['execution_date']}
        Log URL: {context['task_instance'].log_url}
        """
    send_email('alert@example.com', subject, body)


@dag(
    dag_id="monitoring_alerting",
    start_date=datetime.today(),
    schedule_interval=timedelta(days=1)
)
def main_dag():
    start = BashOperator(
        task_id="start",
        bash_command="echo 'Starting the DAG!'"
    )

    failed = BashOperator(
        task_id="failed",
        bash_command="exit 1",
        on_failure_callback=failure_email
    )

    succeed = EmailOperator(
        task_id="succeed",
        to="alert@example.com",
        subject="Task Succeeded",
        html_content="<p>The DAG has completed successfully.</p>"
    )

    start >> [failed, succeed]


dag = main_dag()
