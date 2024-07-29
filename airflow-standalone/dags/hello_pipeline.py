import textwrap
from datetime import datetime, timedelta

from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator

with DAG(
        "hello_pipeline",
        default_args={
            "depends_on_past": False,
            "email": ["airflow@example.com"],
            "email_on_failure": False,
            "email_on_retry": False,
            "retries": 1,
            "retry_delay": timedelta(minutes=5),
        },
        description="A simple tutorial DAG",
        schedule=timedelta(days=1),
        start_date=datetime(2021, 1, 1),
        catchup=False,
        tags=["example"],
) as dag:
    dag.doc_md = __doc__
    dag.doc_md = """
    This is an example for a pipeline DAG.
    """

    t1 = BashOperator(
        task_id="print_date",
        bash_command="date",
    )
    t1.doc_md = textwrap.dedent("""\
    This task print current date and time.
    """)

    t2 = BashOperator(
        task_id="sleep",
        depends_on_past=False,
        bash_command="sleep 5",
        retries=3,
    )

    templated_command = textwrap.dedent("""
    {% for i in range(5) %}
        echo "{{ ds }}"
        echo "{{ macros.ds_add(ds, 7)}}"
    {% endfor %}
    """)

    t3 = BashOperator(
        task_id="templated",
        depends_on_past=False,
        bash_command=templated_command,
    )

    t1 >> [t2, t3]
