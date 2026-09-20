from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np
from matplotlib.figure import Figure  # noqa: E402
from sklearn.metrics import PredictionErrorDisplay


class ArtifactVisualizer:

    @staticmethod
    def save_figure(figure: Figure, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            figure.savefig(output_path)
        finally:
            plt.close(figure)
        return output_path

    @classmethod
    def save_actual_vs_predicted(
            cls,
            y_true,
            y_pred,
            run_id: str,
            audit_dir: Path,
            output_path: Path | None = None,
    ) -> Path:
        display = PredictionErrorDisplay.from_predictions(
            y_true,
            y_pred,
            kind="actual_vs_predicted",
        )
        return cls.save_figure(
            display.figure_,
            output_path if output_path is not None else audit_dir / run_id / "actual_vs_predicted.png",
        )

    @classmethod
    def save_residual_vs_predicted(
            cls,
            y_true,
            y_pred,
            run_id: str,
            audit_dir: Path,
            output_path: Path | None = None,
    ) -> Path:
        display = PredictionErrorDisplay.from_predictions(
            np.asarray(y_true),
            np.asarray(y_pred),
            kind="residual_vs_predicted",
        )
        return cls.save_figure(
            display.figure_,
            output_path if output_path is not None else audit_dir / run_id / "residual_vs_predicted.png",
        )

    @classmethod
    def save_feature_importance(
            cls,
            fitted_model,
            run_id: str,
            audit_dir: Path,
            top_n: int = 20,
            output_path: Path | None = None,
    ) -> Path | None:
        pipeline = getattr(fitted_model, "pipeline", fitted_model)
        regressor = (
            pipeline.named_steps["regressor"]
            if hasattr(pipeline, "named_steps") and "regressor" in pipeline.named_steps
            else pipeline
        )
        importances = getattr(regressor, "feature_importances_", None)
        if importances is None:
            return None

        importances = np.asarray(importances)
        if importances.size == 0:
            return None

        feature_names = cls._feature_names(pipeline, len(importances))
        if feature_names is None:
            return None
        order = np.argsort(importances)[::-1][:top_n]
        figure, axes = plt.subplots()
        axes.barh(np.asarray(feature_names)[order], importances[order])
        axes.invert_yaxis()
        axes.set_xlabel("Importance")
        axes.set_ylabel("Feature")
        axes.set_title("Feature importance")
        figure.tight_layout()
        return cls.save_figure(
            figure,
            output_path if output_path is not None else audit_dir / run_id / "feature_importance.png",
        )

    @staticmethod
    def _feature_names(pipeline, count: int) -> list[str] | None:
        if hasattr(pipeline, "named_steps"):
            preprocessor = pipeline.named_steps.get("preprocessor")
            if preprocessor is not None and hasattr(preprocessor, "get_feature_names_out"):
                names = list(preprocessor.get_feature_names_out())
                if len(names) == count:
                    return names
        return None
