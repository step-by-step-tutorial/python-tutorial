from datetime import datetime, timezone
from pathlib import Path

from ml_prediction.data_model.report import Report


class ReportService:

    def __init__(self, report_dir: Path) -> None:
        self.report_dir = report_dir

    def start(self, dataset: str, operation: str, model_path: Path | None = None) -> Report:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        path = self.report_dir / f"{dataset}_{operation}_report_{timestamp}.csv"
        return Report(path, dataset, operation, model_path)
