import pandas as pd

from ml_prediction.audit.data.audit_operation import AuditOperation
from ml_prediction.audit.execution_log_service_ import ExecutionLogService
from ml_prediction.audit.pipeline_step.dataset_loaded_dto import DatasetLoadedDto
from ml_prediction.audit.pipeline_step.dataset_ready_dto import DatasetReadyDto
from ml_prediction.audit.pipeline_step.model_loaded_dto import ModelLoadedDto
from ml_prediction.audit.pipeline_step.prediction_completed_dto import PredictionCompletedDto
from ml_prediction.audit.pipeline_step.predictions_generated_dto import PredictionsGeneratedDto
from ml_prediction.config.settings import get_settings
from ml_prediction.data_model.prediction_dto import PredictionDto
from ml_prediction.dataset.dataset import Dataset
from ml_prediction.inference.predictor import Predictor
from ml_prediction.utils.id_generator import IdGenerator


class PredictionService:
    def __init__(self, dataset: Dataset, predictor: Predictor[pd.Series]) -> None:
        self.settings = get_settings(dataset.dataset_name)
        self.dataset = dataset
        self.predictor = predictor

    def predict(self) -> PredictionDto:
        dataframe, dataset_path = self.dataset.download()
        predictions = self.predictor.predict(dataframe)

        model_path = self.predictor.model_path
        audit_path = self.settings.prediction_audit_path(IdGenerator.generate())

        if self.settings.execution_log_enabled:
            execution_log_service = ExecutionLogService(self.settings.dataset_name, AuditOperation.PREDICTION)
            execution_log_service.write(DatasetReadyDto(dataset_path), audit_path)
            execution_log_service.write(ModelLoadedDto(model_path), audit_path)
            execution_log_service.write(DatasetLoadedDto(len(dataframe), dataset_path), audit_path)
            execution_log_service.write(PredictionsGeneratedDto(len(predictions), len(dataframe.columns)), audit_path)
            execution_log_service.write(PredictionCompletedDto(audit_path), audit_path)

        return PredictionDto(
            dataframe=dataframe,
            predictions=predictions,
            source_path=dataset_path,
            prediction_column=self.predictor.prediction_column,
            task_type=self.settings.task_type,
            audit_path=audit_path,
        )
