from data_platform.model.pipeline_flow_model import PipelineFlowModel


class _Stage:
    def __init__(self, name): self.name = name


def test_pipeline_flow_keeps_declared_ingestors_in_order() -> None:
    flow = PipelineFlowModel(ingestors=(_Stage("one"), _Stage("two")))
    assert [stage.name for stage in flow.ingestors] == ["one", "two"]


def test_pipeline_flow_allows_empty_defaults() -> None:
    assert PipelineFlowModel().cleaners.clean(None) is None
    assert PipelineFlowModel().validators.validators == ()
    assert PipelineFlowModel().enrichers.enrich(None) is None
    assert PipelineFlowModel().analyzers.analyze(None) == ()
    assert PipelineFlowModel().after_step("ingest") is None
