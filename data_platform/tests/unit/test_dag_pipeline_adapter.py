from data_platform.adapter.dag_pipeline_adapter import DagPipelineAdapter


def test_adapter_delegates_explicit_dag_stages_through_the_pipeline_wrapper(mocker) -> None:
    pipeline = mocker.Mock()
    adapter = DagPipelineAdapter(pipeline)
    pipeline.run_stage.side_effect = [None, ("raw",), ("cleaned",), ("enriched",), None, None, None]

    adapter.prepare()
    raw = adapter.ingest()
    cleaned = adapter.clean(raw)
    enriched = adapter.enrich(cleaned)
    adapter.expose(enriched)
    adapter.analyze(enriched)
    adapter.cleanup()

    assert pipeline.run_stage.call_count == 7
    pipeline.complete.assert_called_once()


