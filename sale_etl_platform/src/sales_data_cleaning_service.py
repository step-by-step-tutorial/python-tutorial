import pandas as pd


class SalesDataCleaningService:
    def clean_sales_data(self, sales_dataframe: pd.DataFrame) -> pd.DataFrame:
        cleaned_sales_dataframe = sales_dataframe.copy()

        cleaned_sales_dataframe["quantity"] = pd.to_numeric(
            cleaned_sales_dataframe["quantity"],
            errors="coerce",
        )

        cleaned_sales_dataframe["unit_price"] = pd.to_numeric(
            cleaned_sales_dataframe["unit_price"],
            errors="coerce",
        )

        cleaned_sales_dataframe["order_date"] = pd.to_datetime(
            cleaned_sales_dataframe["order_date"],
            errors="coerce",
        )

        cleaned_sales_dataframe["quantity"] = cleaned_sales_dataframe[
            "quantity"
        ].fillna(1)

        average_unit_price = cleaned_sales_dataframe["unit_price"].mean()

        cleaned_sales_dataframe["unit_price"] = cleaned_sales_dataframe[
            "unit_price"
        ].fillna(average_unit_price)

        cleaned_sales_dataframe = cleaned_sales_dataframe.dropna(
            subset=["order_date"]
        )

        return cleaned_sales_dataframe