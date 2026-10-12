from pathlib import Path

import pytest


@pytest.mark.parametrize("dag_file, pipeline", [
    ("house_dag.py", 'InmemoryPipeline(dataset_registry.create_dataset("house", PipelineType.INMEMORY))'),
    ("online_shopping_dag.py", 'InmemoryPipeline(dataset_registry.create_dataset("online_shopping", PipelineType.INMEMORY))'),
    ("online_shopping_spark_dag.py", 'SparkPipeline(dataset_registry.create_dataset("online_shopping", PipelineType.SPARK))'),
])
def test_dag_declares_its_dataset_pipeline_adapter_and_standard_chain(dag_file, pipeline) -> None:
    source = (Path(__file__).resolve().parents[2] / "dags" / dag_file).read_text(encoding="utf-8")
    assert "initialize_registries()" in source
    assert pipeline in source
    assert "DagPipelineAdapter(pipeline)" in source
    assert "prepare >> ingest >> clean >> validate >> enrich >> expose >> analyze >> cleanup >> verify" in source
