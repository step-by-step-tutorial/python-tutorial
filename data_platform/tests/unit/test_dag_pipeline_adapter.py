from data_platform.adapter.dag_pipeline_adapter import DagPipelineAdapter


from data_platform.model import StorageObject


def test_adapter_delegates_explicit_dag_stages_through_the_pipeline_wrapper(mocker) -> None:
    pipeline = mocker.Mock()
    adapter = DagPipelineAdapter(pipeline)
    pipeline.run_step.side_effect = [
        None,
        (StorageObject("storage", "raw"),),
        (StorageObject("storage", "cleaned"),),
        (StorageObject("storage", "enriched"),),
        None,
        None,
        None,
    ]

    adapter.prepare()
    raw = adapter.ingest()
    cleaned = adapter.clean(raw)
    enriched = adapter.enrich(cleaned)
    adapter.expose(enriched)
    adapter.analyze(enriched)
    adapter.cleanup()

    assert pipeline.run_step.call_count == 7
    pipeline.start.assert_called_once()
    pipeline.complete.assert_called_once()

