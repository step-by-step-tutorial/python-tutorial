from sales_etl_pipeline_service import SalesEtlPipelineService


def main() -> None:
    sales_etl_pipeline_service = SalesEtlPipelineService()
    sales_etl_pipeline_service.run_pipeline()
    print("Sales ETL pipeline finished successfully.")


if __name__ == "__main__":
    main()