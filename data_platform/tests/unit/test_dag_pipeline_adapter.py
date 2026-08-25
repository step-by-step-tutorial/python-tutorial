from data_platform.adapter.dag_pipeline_adapter import DagPipelineAdapter


def test_adapter_delegates_explicit_dag_stages_through_the_pipeline_wrapper(mocker) -> None:
    pipeline = mocker.Mock()
    adapter = DagPipelineAdapter(pipeline)
    pipeline.run_step.side_effect = [
        None,
        "raw",
        "cleaned",
        "validated",
        "enriched",
        None,
        None,
        None,
    ]

    adapter.prepare()
    raw = adapter.ingest()
    cleaned = adapter.clean(raw)
    validated = adapter.validate(cleaned)
    enriched = adapter.enrich(validated)
    adapter.expose(enriched)
    adapter.analyze(enriched)
    adapter.cleanup()

    assert pipeline.run_step.call_count == 8
    pipeline.start.assert_called_once()
    pipeline.complete.assert_called_once()
