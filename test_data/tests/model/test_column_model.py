from test_data.model.column_model import ColumnModel


def test_column_config_converts_file_columns_to_tuple() -> None:
    column = ColumnModel.from_dict(
        {
            "name": "customer_name",
            "type": "random_from_mapped_file",
            "file_columns": ["first_name_file", "last_name_file"],
        }
    )

    assert column.file_columns == ("first_name_file", "last_name_file")


def test_column_model_list_converter_returns_models() -> None:
    column = ColumnModel.from_dict({"name": "country", "type": "fixed", "value": "USA"})

    assert column == ColumnModel(name="country", type="fixed", value="USA")
