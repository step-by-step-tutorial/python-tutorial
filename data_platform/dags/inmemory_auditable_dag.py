import logging
from datetime import UTC, datetime, timedelta

import pendulum
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG

from app_config import env_config as ec
from model.audit_event import AuditEvent, AuditEventType, AuditStatus
from audit import audit_database_service
from service import pandas_sale_service
from audit.audit_service import AuditService
from audit.audit_task_service import AuditTaskService
from service.database import database_sale_service
from service.datalake import inmemory_datalake_service
from service.datawarehouse import datawarehouse_sale_service
from streaming.audit_event_producer import AuditEventProducer
from util.datalake_utils import DatalakeLayer, generate_relative_path, build_datalake_uri
from util.pipeline_utils import create_pipeline_id

logger = logging.getLogger(__name__)

DAG_ID = "inmemory_auditable_dag"
DAG_START_DATE = pendulum.datetime(2026, 1, 1, tz="UTC")
PIPELINE_NAME = "InmemoryAuditablePipeline"
TASK_ATTEMPT = 1


def generate_pipeline_context() -> dict:
    context = {
        "pipeline_id": create_pipeline_id(),
        "ingestion_time": datetime.now(UTC).isoformat(),
    }

    logger.info(
        "Generated pipeline context with run id %s and ingestion time %s",
        context["pipeline_id"],
        context["ingestion_time"],
    )

    return context


def start_pipeline(pipeline_context: dict) -> None:
    audit_pipeline_service = AuditService()

    event = audit_pipeline_service.pipeline_started(
        pipeline_name=PIPELINE_NAME,
        pipeline_id=pipeline_context["pipeline_id"],
        metadata={"data_file": ec.DATA_FILE},
    )

    audit_database_service.save_event(event, ec.STREAMING_AUDIT_TOPIC)
    audit_pipeline_service.producer.flush()

    logger.info("Started pipeline with run id %s", pipeline_context["pipeline_id"])


def store_raw_data(pipeline_context: dict) -> dict:
    pipeline_id = pipeline_context["pipeline_id"]
    ingestion_time = datetime.fromisoformat(pipeline_context["ingestion_time"])
    raw_data_path = generate_relative_path(DatalakeLayer.RAW, ingestion_time)

    audit_task_service = AuditTaskService()
    producer = AuditEventProducer()

    try:
        with audit_task_service.audit_task(PIPELINE_NAME, pipeline_id, "store_raw_data", TASK_ATTEMPT) as metrics:
            logger.info("Reading data from file %s", ec.DATA_FILE)
            dataframe = pandas_sale_service.read_data(ec.DATA_FILE)

            row_count = len(dataframe)

            metrics.input_row_count = row_count
            metrics.output_row_count = row_count
            metrics.source_system = "csv"
            metrics.source_uri = ec.DATA_FILE
            metrics.destination_system = "datalake"
            metrics.destination_uri = build_datalake_uri(raw_data_path)

            logger.info("Storing raw data in datalake path %s", raw_data_path)
            inmemory_datalake_service.upload(dataframe, ec.DATALAKE_BUCKET_NAME, raw_data_path)

        producer.publish(
            AuditEvent(
                event_type=AuditEventType.DATASET_WRITTEN,
                pipeline_name=PIPELINE_NAME,
                pipeline_id=pipeline_id,
                status=AuditStatus.SUCCEEDED,
                source_system="csv",
                source_uri=ec.DATA_FILE,
                destination_system="datalake",
                destination_uri=build_datalake_uri(raw_data_path),
                output_row_count=row_count,
                metadata={"datalake_layer": DatalakeLayer.RAW},
            )
        )

        return {
            **pipeline_context,
            "raw_data_path": raw_data_path,
            "input_row_count": row_count,
        }
    finally:
        producer.flush()
        audit_task_service.producer.flush()


def clean_data(pipeline_context: dict) -> dict:
    pipeline_id = pipeline_context["pipeline_id"]
    ingestion_time = datetime.fromisoformat(pipeline_context["ingestion_time"])
    raw_data_path = pipeline_context["raw_data_path"]
    cleaned_data_path = generate_relative_path(DatalakeLayer.CLEANED, ingestion_time)

    audit_task_service = AuditTaskService()
    producer = AuditEventProducer()

    try:
        with audit_task_service.audit_task(PIPELINE_NAME, pipeline_id, "clean_data", TASK_ATTEMPT) as metrics:
            logger.info("Reading raw data from datalake path %s", raw_data_path)
            raw_dataframe = inmemory_datalake_service.download(ec.DATALAKE_BUCKET_NAME, raw_data_path)

            input_row_count = len(raw_dataframe)

            logger.info("Cleaning data")
            cleaned_dataframe = pandas_sale_service.clean_data(raw_dataframe)

            output_row_count = len(cleaned_dataframe)
            rejected_row_count = input_row_count - output_row_count

            metrics.input_row_count = input_row_count
            metrics.output_row_count = output_row_count
            metrics.rejected_row_count = rejected_row_count
            metrics.source_system = "datalake"
            metrics.source_uri = build_datalake_uri(raw_data_path)
            metrics.destination_system = "datalake"
            metrics.destination_uri = build_datalake_uri(cleaned_data_path)

            logger.info("Storing cleaned data in datalake path %s", cleaned_data_path)
            inmemory_datalake_service.upload(cleaned_dataframe, ec.DATALAKE_BUCKET_NAME, cleaned_data_path)

        producer.publish(
            AuditEvent(
                event_type=AuditEventType.DATASET_WRITTEN,
                pipeline_name=PIPELINE_NAME,
                pipeline_id=pipeline_id,
                status=AuditStatus.SUCCEEDED,
                source_system="datalake",
                source_uri=build_datalake_uri(raw_data_path),
                destination_system="datalake",
                destination_uri=build_datalake_uri(cleaned_data_path),
                output_row_count=output_row_count,
                metadata={"datalake_layer": DatalakeLayer.CLEANED},
            )
        )

        return {
            **pipeline_context,
            "cleaned_data_path": cleaned_data_path,
            "cleaned_row_count": output_row_count,
            "rejected_row_count": rejected_row_count,
        }
    finally:
        producer.flush()
        audit_task_service.producer.flush()


def enrich_data(pipeline_context: dict) -> dict:
    pipeline_id = pipeline_context["pipeline_id"]
    ingestion_time = datetime.fromisoformat(pipeline_context["ingestion_time"])
    cleaned_data_path = pipeline_context["cleaned_data_path"]
    enriched_data_path = generate_relative_path(DatalakeLayer.ENRICHED, ingestion_time)

    audit_task_service = AuditTaskService()
    producer = AuditEventProducer()

    try:
        with audit_task_service.audit_task(PIPELINE_NAME, pipeline_id, "enrich_data", TASK_ATTEMPT) as metrics:
            logger.info("Reading cleaned data from datalake path %s", cleaned_data_path)
            cleaned_dataframe = inmemory_datalake_service.download(ec.DATALAKE_BUCKET_NAME, cleaned_data_path)

            input_row_count = len(cleaned_dataframe)

            logger.info("Enriching data")
            enriched_dataframe = pandas_sale_service.enrich_data(cleaned_dataframe)

            output_row_count = len(enriched_dataframe)

            metrics.input_row_count = input_row_count
            metrics.output_row_count = output_row_count
            metrics.source_system = "datalake"
            metrics.source_uri = build_datalake_uri(cleaned_data_path)
            metrics.destination_system = "datalake"
            metrics.destination_uri = build_datalake_uri(enriched_data_path)

            logger.info("Storing enriched data in datalake path %s", enriched_data_path)
            inmemory_datalake_service.upload(enriched_dataframe, ec.DATALAKE_BUCKET_NAME, enriched_data_path)

        producer.publish(
            AuditEvent(
                event_type=AuditEventType.DATASET_WRITTEN,
                pipeline_name=PIPELINE_NAME,
                pipeline_id=pipeline_id,
                status=AuditStatus.SUCCEEDED,
                source_system="datalake",
                source_uri=build_datalake_uri(cleaned_data_path),
                destination_system="datalake",
                destination_uri=build_datalake_uri(enriched_data_path),
                output_row_count=output_row_count,
                metadata={"datalake_layer": DatalakeLayer.ENRICHED},
            )
        )

        return {
            **pipeline_context,
            "enriched_data_path": enriched_data_path,
            "output_row_count": output_row_count,
        }
    finally:
        producer.flush()
        audit_task_service.producer.flush()


def populate_database(pipeline_context: dict) -> None:
    pipeline_id = pipeline_context["pipeline_id"]
    enriched_data_path = pipeline_context["enriched_data_path"]
    audit_task_service = AuditTaskService()

    try:
        dataframe = inmemory_datalake_service.download(ec.DATALAKE_BUCKET_NAME, enriched_data_path)

        with audit_task_service.audit_task(PIPELINE_NAME, pipeline_id, "populate_database", TASK_ATTEMPT) as metrics:
            row_count = len(dataframe)

            metrics.input_row_count = row_count
            metrics.output_row_count = row_count
            metrics.source_system = "dataframe"
            metrics.source_uri = "enriched_dataframe"
            metrics.destination_system = "postgresql"
            metrics.destination_uri = ec.DATABASE_STAGE_TABLE_NAME

            logger.info("Populating operational database with enriched data")
            database_sale_service.populate(dataframe)
    finally:
        audit_task_service.producer.flush()


def populate_datawarehouse(pipeline_context: dict) -> None:
    pipeline_id = pipeline_context["pipeline_id"]
    enriched_data_path = pipeline_context["enriched_data_path"]
    audit_task_service = AuditTaskService()

    try:
        dataframe = inmemory_datalake_service.download(ec.DATALAKE_BUCKET_NAME, enriched_data_path)

        with audit_task_service.audit_task(PIPELINE_NAME, pipeline_id, "populate_datawarehouse",
                                           TASK_ATTEMPT) as metrics:
            row_count = len(dataframe)

            metrics.input_row_count = row_count
            metrics.output_row_count = row_count
            metrics.source_system = "dataframe"
            metrics.source_uri = "enriched_dataframe"
            metrics.destination_system = "clickhouse"
            metrics.destination_uri = ec.DATAWAREHOUSE_NAME

            logger.info("Populating data warehouse with enriched data")
            datawarehouse_sale_service.populate(dataframe)
    finally:
        audit_task_service.producer.flush()


def complete_pipeline(pipeline_context: dict) -> None:
    audit_pipeline_service = AuditService()

    try:
        audit_pipeline_service.pipeline_completed(
            pipeline_name=PIPELINE_NAME,
            pipeline_id=pipeline_context["pipeline_id"],
            input_row_count=pipeline_context["input_row_count"],
            output_row_count=pipeline_context["output_row_count"],
            rejected_row_count=pipeline_context["rejected_row_count"],
            metadata={
                "raw_path": pipeline_context["raw_data_path"],
                "cleaned_path": pipeline_context["cleaned_data_path"],
                "enriched_path": pipeline_context["enriched_data_path"],
                "cleaned_row_count": pipeline_context["cleaned_row_count"],
            },
        )

        logger.info("Pipeline completed successfully with run id %s", pipeline_context["pipeline_id"])
    finally:
        audit_pipeline_service.producer.flush()


with DAG(
        dag_id=DAG_ID,
        description="Run the auditable in-memory ETL pipeline",
        schedule=None,
        start_date=DAG_START_DATE,
        catchup=False,
        max_active_runs=1,
        default_args={
            "owner": "data-platform",
            "retries": 0,
            "retry_delay": timedelta(minutes=1),
        },
        tags={"inmemory", "audit", "etl", "datalake"},
) as dag:
    generate_pipeline_context_task = PythonOperator(
        task_id="generate_pipeline_context",
        python_callable=generate_pipeline_context,
    )

    start_pipeline_task = PythonOperator(
        task_id="start_pipeline",
        python_callable=start_pipeline,
        op_kwargs={"pipeline_context": generate_pipeline_context_task.output},
    )

    store_raw_data_task = PythonOperator(
        task_id="store_raw_data",
        python_callable=store_raw_data,
        op_kwargs={"pipeline_context": generate_pipeline_context_task.output},
    )

    clean_data_task = PythonOperator(
        task_id="clean_data",
        python_callable=clean_data,
        op_kwargs={"pipeline_context": store_raw_data_task.output},
    )

    enrich_data_task = PythonOperator(
        task_id="enrich_data",
        python_callable=enrich_data,
        op_kwargs={"pipeline_context": clean_data_task.output},
    )

    populate_database_task = PythonOperator(
        task_id="populate_database",
        python_callable=populate_database,
        op_kwargs={"pipeline_context": enrich_data_task.output},
    )

    populate_datawarehouse_task = PythonOperator(
        task_id="populate_datawarehouse",
        python_callable=populate_datawarehouse,
        op_kwargs={"pipeline_context": enrich_data_task.output},
    )

    complete_pipeline_task = PythonOperator(
        task_id="complete_pipeline",
        python_callable=complete_pipeline,
        op_kwargs={"pipeline_context": enrich_data_task.output},
    )

    generate_pipeline_context_task >> start_pipeline_task >> store_raw_data_task >> clean_data_task >> enrich_data_task

    enrich_data_task >> [
        populate_database_task,
        populate_datawarehouse_task,
    ]

    [
        populate_database_task,
        populate_datawarehouse_task,
    ] >> complete_pipeline_task
