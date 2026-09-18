from ml_prediction.utils.id_generator import IdGenerator

import pandas as pd

from ml_prediction.audit.pipeline_step.dataset_loaded_data import DatasetLoadedData
from ml_prediction.audit.pipeline_step.dataset_ready_data import DatasetReadyData
from ml_prediction.audit.pipeline_step.model_loaded_data import ModelLoadedData
from ml_prediction.audit.pipeline_step.prediction_completed_data import PredictionCompletedData
from ml_prediction.audit.pipeline_step.predictions_generated_data import PredictionsGeneratedData
from ml_prediction.audit.execution_log_service import ExecutionLogService
from ml_prediction.audit.data.audit_operation import AuditOperation
from ml_prediction.config.settings import get_settings
from ml_prediction.data_model.prediction import Prediction
from ml_prediction.dataset.dataset import Dataset
from ml_prediction.inference.predictor import Predictor


class PredictionService:
    def __init__(self, predictor: Predictor[pd.Series], dataset: Dataset) -> None:
        self.settings = get_settings(dataset.dataset_name)
        self.predictor = predictor
        self.dataset = dataset
        self.audit_dir = self.settings.audit_dir

    def predict(self) -> Prediction:
        model_path = self.predictor.model_path
        dataframe, dataset_path = self.dataset.download()

        audit_path = self.settings.prediction_audit_path(IdGenerator.generate())
        execution_log_service = ExecutionLogService(self.settings.dataset_name, AuditOperation.PREDICTION)
        execution_log_service.write(DatasetReadyData(dataset_path), audit_path)
        execution_log_service.write(ModelLoadedData(model_path), audit_path)

        execution_log_service.write(DatasetLoadedData(len(dataframe), dataset_path), audit_path)
        predictions = self.predictor.predict(dataframe)
        execution_log_service.write(PredictionsGeneratedData(len(predictions), len(dataframe.columns)), audit_path)
        execution_log_service.write(PredictionCompletedData(audit_path), audit_path)

        return Prediction(
            dataframe,
            predictions,
            dataset_path,
            audit_path,
            self.predictor.prediction_column,
        )
