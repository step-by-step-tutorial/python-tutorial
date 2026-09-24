from pathlib import Path

import matplotlib.pyplot as plt

from ml_prediction.visualize.classification_evaluation_visualizer import ClassificationEvaluationVisualizer


def test_save_confusion_matrix_creates_artifact(tmp_path: Path, mocker) -> None:
    settings = mocker.Mock(confusion_matrix_filename="confusion_matrix.png")
    settings.artifact_path.side_effect = lambda run_id, filename: tmp_path / run_id / filename
    mocker.patch(
        "ml_prediction.visualize.classification_evaluation_visualizer.get_settings",
        return_value=settings,
    )
    visualizer = ClassificationEvaluationVisualizer("online_shopping")

    output_path = visualizer.save_confusion_matrix(
        ["completed", "completed", "cancelled"],
        ["completed", "cancelled", "cancelled"],
        "experiment-1",
    )

    assert output_path == tmp_path / "experiment-1" / "confusion_matrix.png"
    assert output_path.exists()
    assert plt.get_fignums() == []
