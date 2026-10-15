import mlflow
import mlflow.sklearn

from ml_platform.model.artifact_model import ArtifactModel
from ml_platform.model.settings_model import SettingsModel
from ml_platform.model.training_result_model import TrainingResultModel


class MlflowService:
    def __init__(self, settings: SettingsModel) -> None:
        self._settings = settings
        mlflow.set_tracking_uri(settings.mlflow.tracking_uri)
        mlflow.set_experiment(f"{settings.mlflow.experiment_prefix}/{settings.dataset_name}")

    def publish(self, result: TrainingResultModel, artifacts: tuple[ArtifactModel, ...]) -> None:
        experiment = result.experiment
        with mlflow.start_run(run_name=experiment.run_id):
            mlflow.set_tags({
                "dataset_name": experiment.dataset_name,
                "task_type": experiment.task_type.value,
                "model_type": experiment.model_type,
            })
            mlflow.log_params(experiment.model_parameters)
            mlflow.log_metrics(experiment.to_metrics())
            mlflow.sklearn.log_model(result.pipeline, name="model", serialization_format="cloudpickle")
            for artifact in artifacts:
                mlflow.log_artifact(str(artifact.path), artifact_path=artifact.category.value)
