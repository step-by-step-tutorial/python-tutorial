from src import config
from src.loader import load_csv
from src.cleaner import clean_sales_data
from src.transformer import transform_sales_data
from src.reporter import build_report, save_report


def main():
    print("Loading data")
    df = load_csv(config.CSV_PATH)

    print("Cleaning data")
    df = clean_sales_data(df)

    print("Transforming data")
    df = transform_sales_data(df)

    print("Saving cleaned data")
    df.to_csv(config.CLEANED_DATA_OUTPUT_PATH, index=False)

    print("Building report")
    report = build_report(df)

    print(report)

    print("Saving report")
    save_report(report, config.REPORT_OUTPUT_PATH)

    print("Program finished successfully.")


if __name__ == "__main__":
    main()
