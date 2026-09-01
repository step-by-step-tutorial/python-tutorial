from ml_prediction.config.classification_search import CLASSIFICATION_PARAMETER_GRID
from ml_prediction.config.regression_search import REGRESSION_PARAMETER_GRID
from ml_prediction.model_selection.classification_model_selector import ClassificationModelSelector
from ml_prediction.model_selection.regression_model_selector import RegressionModelSelector


def test_regression_model_selector_uses_regression_grid_and_mae(mocker) -> None:
    grid_search_class = mocker.patch(
        "ml_prediction.model_selection.regression_model_selector.GridSearchCV"
    )
    search = grid_search_class.return_value
    search.best_estimator_ = mocker.Mock()
    search.best_params_ = {"regressor__n_estimators": 300}
    search.best_score_ = -12.5
    search.cv_results_ = {
        "params": [{"regressor__n_estimators": 300}],
        "mean_test_score": [-12.5],
    }

    result = RegressionModelSelector().select(mocker.Mock(), [1], [2])

    grid_search_class.assert_called_once_with(
        estimator=mocker.ANY,
        param_grid=REGRESSION_PARAMETER_GRID,
        scoring="neg_mean_absolute_error",
        cv=3,
        n_jobs=-1,
        refit=True,
    )
    assert result.parameters == {"regressor__n_estimators": 300}
    assert result.mean_absolute_error == 12.5


def test_classification_model_selector_uses_classification_grid_and_f1(mocker) -> None:
    grid_search_class = mocker.patch(
        "ml_prediction.model_selection.classification_model_selector.GridSearchCV"
    )
    search = grid_search_class.return_value
    search.best_estimator_ = mocker.Mock()
    search.best_params_ = {"classifier__n_estimators": 300}
    search.best_score_ = 0.82
    search.cv_results_ = {
        "params": [{"classifier__n_estimators": 300}],
        "mean_test_score": [0.82],
    }

    result = ClassificationModelSelector().select(mocker.Mock(), [1], [2])

    grid_search_class.assert_called_once_with(
        estimator=mocker.ANY,
        param_grid=CLASSIFICATION_PARAMETER_GRID,
        scoring="f1_weighted",
        cv=3,
        n_jobs=-1,
        refit=True,
    )
    assert result.parameters == {"classifier__n_estimators": 300}
    assert result.f1_score == 0.82
