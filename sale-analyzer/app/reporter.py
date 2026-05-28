import pandas as pd
from pathlib import Path

from app.analyzer import (
    calculate_total_revenue,
    calculate_average_order_value,
    revenue_by_category,
    revenue_by_country,
    top_products_by_quantity,
)


def build_report(df: pd.DataFrame) -> str:
    report = []

    report.append("Sales Data Analysis Report")
    report.append("=" * 40)

    report.append(f"Total Revenue: {calculate_total_revenue(df):.2f}")
    report.append(f"Average Order Value: {calculate_average_order_value(df):.2f}")

    report.append("")
    report.append("Revenue by Category:")
    report.append(str(revenue_by_category(df)))

    report.append("")
    report.append("Revenue by Country:")
    report.append(str(revenue_by_country(df)))

    report.append("")
    report.append("Top Products by Quantity:")
    report.append(str(top_products_by_quantity(df)))

    return "\n".join(report)


def save_report(report: str, output_path: str) -> None:
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(report)
