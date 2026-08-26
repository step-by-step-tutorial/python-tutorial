from pathlib import Path


def test_only_shared_pipeline_classes_and_no_execution_mode_registry_remain() -> None:
    source_root = Path(__file__).resolve().parents[2] / "src" / "data_platform"
    pipeline_files = sorted(path.name for path in (source_root / "pipeline").glob("*pipeline.py"))

    assert pipeline_files == ["data_pipeline.py", "pipeline.py", "spark_pipeline.py"]
    assert not (source_root / "registry" / "ingestor_registry.py").exists()
    assert "pipeline_type" not in (source_root / "config" / "app_settings.py").read_text(encoding="utf-8")

