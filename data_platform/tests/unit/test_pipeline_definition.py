from pathlib import Path

import pytest

from data_platform.model.pipeline_flow import PipelineFlow


class _Stage:
    def __init__(self, name): self.name = name
    def ingest(self, run): return ()
    def clean(self, run, paths): return paths
    def enrich(self, run, paths): return paths
    def expose(self, run, paths): return paths
    def analyze(self, run, paths): return paths


def _factory(service):
    return lambda context: service


def test_pipeline_steps_owns_explicit_stage_factories_in_declared_order() -> None:
    definition = PipelineFlow(
        repository=_factory(object()),
        ingestors=(_Stage("one"), _Stage("two")),
        cleaners=_Stage("clean"),
        validators=None,
        enrichers=_Stage("enrich"),
        exposers=(_Stage("expose"),),
    )
    assert [stage.name for stage in definition.ingestors] == ["one", "two"]


def test_pipeline_steps_accepts_declared_ingestors() -> None:
    class StorageDouble:
        def save(self, data, path): return path
        def find(self, path): return None

    PipelineFlow(StorageDouble(), (_Stage("same"), _Stage("same")), (_Stage("clean"),), (_Stage("enrich"),))


def test_pipeline_steps_allows_empty_defaults() -> None:
    assert PipelineFlow().cleaners.clean(None) is None
    assert PipelineFlow().validators.validators == ()
    assert PipelineFlow().enrichers.enrich(None) is None
    assert PipelineFlow().analyzers.analyze(None) == ()


@pytest.mark.parametrize("module_path", ["domain/house/dataset.py", "domain/online_shopping/dataset.py"])
def test_dataset_module_constructs_its_dataset_once_without_self_reference(module_path) -> None:
    source = (Path(__file__).resolve().parents[2] / "src" / "data_platform" / module_path).read_text(encoding="utf-8")
    dataset_name = {"domain/house/dataset.py": "house_dataset", "domain/online_shopping/dataset.py": "ONLINE_SHOPPING_DATASET"}[module_path]
    assert source.count(f"{dataset_name} = Dataset(") == 1
    assert "replace(" not in source
    assert f"{dataset_name}.get_endpoint(" not in source


def test_removed_vague_stage_factory_helpers_do_not_exist() -> None:
    source_root = Path(__file__).resolve().parents[2] / "src" / "data_platform"
    assert not (source_root / "pipeline" / "stage_factories.py").exists()
