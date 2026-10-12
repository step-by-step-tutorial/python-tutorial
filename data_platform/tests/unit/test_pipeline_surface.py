from pathlib import Path


def test_pipeline_package_holds_one_class_per_execution_engine() -> None:
    source_root = Path(__file__).resolve().parents[2] / "src" / "data_platform"
    pipeline_files = sorted(path.name for path in (source_root / "pipeline").glob("*pipeline.py"))

    assert pipeline_files == ["inmemory_pipeline.py", "pipeline.py", "spark_pipeline.py"]
