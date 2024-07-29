import pytest
from airflow.models import DagBag


@pytest.fixture()
def dagbag():
    dag_bag = DagBag(dag_folder='/opt/airflow/dags', include_examples=False)
    assert len(dag_bag.import_errors) == 0, 'No DAG loading errors'
    return dag_bag


def test_given_dag_then_return_task_no(dagbag):
    given_dag_id = "hello_world"

    actual = dagbag.get_dag(dag_id=given_dag_id)

    assert actual is not None
    assert len(actual.tasks) == 1
