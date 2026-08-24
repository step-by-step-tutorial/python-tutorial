from pathlib import Path

import pytest


@pytest.mark.parametrize("dag_file, dataset_name", [
    ("sale_dag.py", "SALE_DATASET"),
    ("house_dag.py", "HOUSE_DATASET"),
    ("online_shopping_dag.py", "ONLINE_SHOPPING_DATASET"),
])
def test_dag_declares_its_dataset_pipeline_adapter_and_standard_chain(dag_file, dataset_name) -> None:
    source = (Path(__file__).resolve().parents[2] / "dags" / dag_file).read_text(encoding="utf-8")
    assert f"ConfiguredPipeline({dataset_name})" in source
    assert "DagPipelineAdapter(pipeline)" in source
    assert 'prepare >> ingest >> clean >> enrich >> expose >> analyze >> cleanup >> verify' in source


def test_dag_factory_and_task_runner_are_removed() -> None:
    airflow_source = Path(__file__).resolve().parents[2] / "src" / "data_platform" / "airflow"
    assert not (airflow_source / "dag_factory.py").exists()
    assert not (airflow_source / "task_runner.py").exists()


