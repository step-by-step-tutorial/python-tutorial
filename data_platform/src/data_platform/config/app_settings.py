import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppSettings:
    dataset_name: str
    root: Path
    resources_dir: str
    output_dir: Path
    scripts_dir: Path
    spark_dir: Path
    data_file: str


app = AppSettings(
    dataset_name=os.getenv("DATASET_NAME", "Sale"),
    root=Path(os.getenv("ROOT", Path(__file__).resolve().parents[3])),
    resources_dir=os.getenv("RESOURCES_DIR", "resources"),
    output_dir=Path(os.getenv("OUTPUT_DIR", "output")),
    scripts_dir=Path(os.getenv("SCRIPTS_DIR", "scripts")),
    spark_dir=Path(os.getenv("SPARK_DIR", "spark")),
    data_file=os.getenv("DATA_FILE", "sale.csv"),
)

