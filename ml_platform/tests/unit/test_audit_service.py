from datetime import datetime, timezone

from conftest import make_settings
from ml_platform.audit.audit_service import AuditService
from ml_platform.config.dataset_profiles import HOUSE
from ml_platform.config.operation import Operation
from ml_platform.model.execution_model import ExecutionModel
from ml_platform.model.metrics_model import RegressionMetricsModel
from ml_platform.util.csv_utils import read_rows


def test_log_step_appends_execution_rows(tmp_path) -> None:
    audit = AuditService(make_settings(tmp_path, HOUSE), Operation.TRAIN)
    metrics = RegressionMetricsModel(mean_absolute_error=1.0, root_mean_squared_error=2.0, r2_score=0.5)

    audit.log_step("dataset_loaded", rows=10)
    audit.log_step("model_evaluated", partition="test", rows=3, metrics=metrics)

    executions = read_rows(audit.execution_log_path, ExecutionModel.from_dict)
    assert [execution.step for execution in executions] == ["dataset_loaded", "model_evaluated"]
    assert executions[1].metrics == metrics.to_dict()
    assert {execution.run_id for execution in executions} == {audit.run_id}


def test_disabled_audit_writes_nothing(tmp_path) -> None:
    settings = make_settings(tmp_path, HOUSE, execution_log_enabled=False, experiment_enabled=False)
    audit = AuditService(settings, Operation.PREDICT)

    audit.log_step("model_loaded")

    assert not settings.audit_dir.exists()


def test_execution_model_round_trip() -> None:
    execution = ExecutionModel(
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
        run_id="run",
        dataset_name="house",
        operation=Operation.TRAIN,
        step="model_saved",
        partition="",
        rows=None,
        model_name="random_forest",
        model_path="models/house_model.joblib",
        model_id="abc",
        metrics={"r2_score": 0.5},
        details="",
    )

    values = {name: "" if value is None else str(value) for name, value in execution.to_dict().items()}

    assert ExecutionModel.from_dict(values) == execution
