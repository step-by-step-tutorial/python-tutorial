import pytest
from airflow.models import DagBag


@pytest.fixture()
def dagbag():
    dag_bag = DagBag(dag_folder='/opt/airflow/dags', include_examples=False)
    assert len(dag_bag.import_errors) == 0, 'No DAG loading errors'
    return dag_bag


def test_given_dag_include_bash_operation_then_return_task_no(dagbag):
    given_dag_id = "bash_dependency"

    actual = dagbag.get_dag(dag_id=given_dag_id)

    assert actual is not None
    assert len(actual.tasks) == 4


def test_given_dag_include_python_operation_then_return_task_no(dagbag):
    given_dag_id = "python_dependency"

    actual = dagbag.get_dag(dag_id=given_dag_id)

    assert actual is not None
    assert len(actual.tasks) == 4
