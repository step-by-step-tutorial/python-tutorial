import pytest

from util.spark_utils import batch_rows, collect_rows

pytestmark = pytest.mark.unit


class TestCollectRows:

    def test_should_collect_rows_using_dataframe_column_order(self, mocker) -> None:
        class _Row:
            def __init__(self, value: int, name: str) -> None:
                self.value = value
                self.name = name

            def asDict(self, recursive: bool = True):
                return {"value": self.value, "name": self.name}

        dataframe = mocker.Mock()
        dataframe.columns = ["name", "value"]
        dataframe.collect.return_value = [_Row(1, "A"), _Row(2, "B")]

        actual = collect_rows(dataframe)

        assert actual == [("A", 1), ("B", 2)]


class TestBatchRows:

    def test_should_split_rows_into_batches(self) -> None:
        rows = [(1,), (2,), (3,)]

        actual = batch_rows(rows, batch_size=2)

        assert actual == [[(1,), (2,)], [(3,)]]
