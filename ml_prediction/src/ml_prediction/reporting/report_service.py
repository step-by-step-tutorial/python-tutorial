from datetime import datetime, timezone

from ml_prediction.offline_tracking.report_writer import ReportWriter


class ReportService:

    def __init__(self, report_dir):
        self.report_dir = report_dir

    def start(self, dataset: str, operation: str, model_path=None, run_id: str = "") -> ReportWriter:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        path = self.report_dir / f"{dataset}_{operation}_report_{timestamp}.csv"
        return ReportWriter(path, dataset, operation, model_path, run_id)
