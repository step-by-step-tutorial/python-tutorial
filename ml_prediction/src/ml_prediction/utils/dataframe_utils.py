import pandas as pd

from ml_prediction.utils.data_validator_utils import require_blank


def should_have_unique_columns(dataframe: pd.DataFrame) -> None:
    if dataframe.empty:
        raise Exception("DataFrame must not be empty")

    duplicated_columns = dataframe.columns[dataframe.columns.duplicated()].tolist()
    require_blank(duplicated_columns, f"DataFrame contains duplicated column names: {duplicated_columns}")
