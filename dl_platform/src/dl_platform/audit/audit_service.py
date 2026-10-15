from datetime import datetime, timezone
from uuid import uuid4

from dl_platform.model.execution_model import ExecutionModel
from dl_platform.model.settings_model import SettingsModel
from dl_platform.util.csv_utils import append_rows


class AuditService:
    def __init__(self, settings: SettingsModel) -> None:
        self._settings = settings
        self.run_id = str(uuid4())
        self.execution_log_path = settings.execution_log_path(self.run_id)

    def log_step(self, step: str, *, rows: int | None = None, details: str = "") -> None:
        if not self._settings.execution_log_enabled:
            return
        execution = ExecutionModel(
            timestamp=datetime.now(timezone.utc),
            run_id=self.run_id,
            task_name=self._settings.task.name,
            step=step,
            rows=rows,
            details=details,
        )
        append_rows(self.execution_log_path, [execution.to_dict()])
