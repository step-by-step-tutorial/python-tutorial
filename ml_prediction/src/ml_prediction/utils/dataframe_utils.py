import pandas as pd

from ml_prediction.utils.data_validator_utils import should_be_blank


def extract(dataframe: pd.DataFrame, columns) -> pd.DataFrame:
    return dataframe.loc[:, columns].copy()


def should_have_unique_columns(dataframe: pd.DataFrame) -> None:
    if dataframe.empty:
        raise Exception("DataFrame must not be empty")

    duplicated_columns = dataframe.columns[dataframe.columns.duplicated()].tolist()
    should_be_blank(duplicated_columns, f"DataFrame contains duplicated column names: {duplicated_columns}")
