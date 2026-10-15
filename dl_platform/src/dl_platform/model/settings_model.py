import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from dl_platform.config.model_type import ModelType
from dl_platform.model.detection_task_model import DetectionTaskModel
from dl_platform.util.type_utils import to_bool

DEFAULT_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class SettingsModel:
    task: DetectionTaskModel
    data_dir: Path
    model_dir: Path
    output_dir: Path
    audit_dir: Path
    model_type: ModelType = ModelType.FASTER_RCNN_MOBILENET
    device: str = "cpu"
    score_threshold: float = 0.5
    execution_log_enabled: bool = True
    coco_dir: Path | None = None
    evaluation_images: int = 100

    @classmethod
    def from_env(cls, task: DetectionTaskModel, environ: Mapping[str, str] | None = None) -> "SettingsModel":
        environ = os.environ if environ is None else environ
        root = Path(environ.get("PROJECT_ROOT", DEFAULT_ROOT))
        return cls(
            task=task,
            data_dir=Path(environ.get("DL_PLATFORM_DATA_DIR", root / "data")),
            model_dir=Path(environ.get("DL_PLATFORM_MODEL_DIR", root / "models")),
            output_dir=Path(environ.get("DL_PLATFORM_OUTPUT_DIR", root / "output")),
            audit_dir=Path(environ.get("DL_PLATFORM_AUDIT_DIR", root / "audit_log")),
            model_type=ModelType(environ.get("DL_PLATFORM_MODEL_TYPE", ModelType.FASTER_RCNN_MOBILENET)),
            device=environ.get("DL_PLATFORM_DEVICE", "cpu"),
            score_threshold=float(environ.get("DL_PLATFORM_SCORE_THRESHOLD", task.score_threshold)),
            execution_log_enabled=to_bool(environ.get("EXECUTION_LOG_ENABLED"), default=True),
            coco_dir=Path(environ["DL_PLATFORM_COCO_DIR"]) if "DL_PLATFORM_COCO_DIR" in environ else None,
            evaluation_images=int(environ.get("DL_PLATFORM_EVALUATION_IMAGES", 100)),
        )

    @property
    def input_dir(self) -> Path:
        return self.data_dir / self.task.name

    @property
    def annotated_dir(self) -> Path:
        return self.output_dir / self.task.name

    @property
    def detections_path(self) -> Path:
        return self.output_dir / f"{self.task.name}_detections.csv"

    @property
    def coco_path(self) -> Path:
        return self.coco_dir if self.coco_dir is not None else self.data_dir / "coco"

    @property
    def evaluation_path(self) -> Path:
        return self.output_dir / f"{self.task.name}_evaluation.csv"

    def execution_log_path(self, run_id: str, operation: str = "detect") -> Path:
        return self.audit_dir / f"{self.task.name}_{operation}_{run_id}.csv"
