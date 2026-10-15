from test_data_platform.generator.column.column_generator import ColumnGenerator, Row
from test_data_platform.util.validation_utils import default_if_blank, require_not_blank


class SequenceColumn(ColumnGenerator):

    def generate(self, row: Row, row_index: int) -> str:
        return str(default_if_blank(self.model.start, 1) + row_index * default_if_blank(self.model.step, 1))


class FixedColumn(ColumnGenerator):

    def validate(self) -> None:
        self.require("value")

    def generate(self, row: Row, row_index: int) -> str:
        return str(require_not_blank(self.model.value))
