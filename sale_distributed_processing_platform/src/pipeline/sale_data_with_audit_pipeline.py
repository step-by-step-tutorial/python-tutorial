import logging
import time
from datetime import UTC, datetime

import pandas as pd
from itables import show

from app_config import env_config as ec
from model.audit_event import AuditEvent, AuditEventType, AuditStatus
from repository import audit_repository
from service import csv_sale_service as csv_service
from service.audit.audit_pipeline_service import AuditPipelineService
from service.audit.audit_task_service import AuditTaskService
from service.database import database_sale_service as database_service
from service.datalake import datalake_pandas_sale_service as datalake_service
from service.datawarehouse import datawarehouse_sale_service
from streaming.audit_event_producer import AuditEventProducer
from util.datalake_utils import DatalakeLayer, build_sale_datalake_path, build_datalake_uri
from util.log_utils import draw_line
from util.pipeline_utils import create_pipeline_id
from util.time_utils import elapsed_milliseconds

logger = logging.getLogger(__name__)

PIPELINE_NAME = "sale_data_with_audit_pipeline"
TASK_ATTEMPT = 1

producer = AuditEventProducer()
audit_pipeline_service = AuditPipelineService()
audit_task_service = AuditTaskService()
pipeline_id = create_pipeline_id()


def run() -> None:
    started_at = time.perf_counter()

    try:
        pipeline_started_event = audit_pipeline_service.pipeline_started(
            pipeline_name=PIPELINE_NAME,
            pipeline_id=pipeline_id,
            metadata={"data_file": ec.DATA_FILE}
        )
        audit_repository.save_event(pipeline_started_event, ec.KAFKA_AUDIT_TOPIC)
        ingestion_time = datetime.now(UTC)
        logger.info("Start pipeline with run-id %s at %s", pipeline_id, ingestion_time)
        draw_line()

        raw_path, total_row_count = upload_raw_data(ingestion_time=ingestion_time)
        logger.info("Upload raw data to %s", raw_path)
        draw_line()

        cleaned_path, cleaned_row_count, rejected_row_count = clean_sale_data(raw_path, ingestion_time)
        logger.info("Upload cleaned data to %s", cleaned_path)
        draw_line()

        enriched_path, enriched_row_count = enrich_sale_data(cleaned_path, ingestion_time)
        logger.info("Upload enriched data to %s", enriched_path)
        draw_line()

        enriched_dataframe = read_enriched_sale_data(enriched_path)
        logger.info("Read enriched data from %s", enriched_path)
        draw_line()

        populate_database(enriched_dataframe)
        logger.info("Populate database with enriched data")
        draw_line()

        populate_datawarehouse(enriched_dataframe)
        logger.info("Populate datawarehouse with enriched data")
        draw_line()

        show_data(enriched_dataframe)
        draw_line()

        process_data_by_csv(enriched_dataframe)
        draw_line()
        process_data_by_datawarehouse()
        draw_line()

        audit_pipeline_service.pipeline_completed(
            pipeline_name=PIPELINE_NAME,
            pipeline_id=pipeline_id,
            input_row_count=total_row_count,
            output_row_count=enriched_row_count,
            rejected_row_count=rejected_row_count,
            duration_ms=elapsed_milliseconds(started_at),
            metadata={
                "raw_path": raw_path,
                "cleaned_path": cleaned_path,
                "enriched_path": enriched_path,
                "cleaned_row_count": cleaned_row_count,
            },
        )

        end_time = time.perf_counter()
        logger.info("Completed pipeline with run-id %s at %s", pipeline_id, end_time)
    except Exception as error:
        audit_pipeline_service.pipeline_failed(
            pipeline_name=PIPELINE_NAME,
            pipeline_id=pipeline_id,
            error=error,
            duration_ms=elapsed_milliseconds(started_at)
        )
        raise
    finally:
        flush_producers(audit_pipeline_service.producer, audit_task_service.producer)


def upload_raw_data(ingestion_time: datetime) -> tuple[str, int]:
    path = build_sale_datalake_path(DatalakeLayer.RAW, ingestion_time)

    with (audit_task_service.audit_task(PIPELINE_NAME, pipeline_id, "upload_raw_data", TASK_ATTEMPT) as metrics):
        dataframe = csv_service.read_data(ec.DATA_FILE)
        total_rows = len(dataframe)

        metrics.input_row_count = total_rows
        metrics.output_row_count = total_rows
        metrics.source_system = "csv"
        metrics.source_uri = ec.DATA_FILE
        metrics.destination_system = "datalake"
        metrics.destination_uri = build_datalake_uri(path)

        datalake_service.upload_parquet(dataframe, ec.DATALAKE_BUCKET_NAME, path)

    publish_written_event(
        source="csv",
        source_uri=ec.DATA_FILE,
        destination_uri=path,
        row_count=total_rows,
        layer=DatalakeLayer.RAW
    )
    draw_line()
    return path, total_rows


def clean_sale_data(raw_path: str, ingestion_time: datetime) -> tuple[str, int, int]:
    cleaned_path = build_sale_datalake_path(DatalakeLayer.CLEANED, ingestion_time)
    with (audit_task_service.audit_task(PIPELINE_NAME, pipeline_id, "clean_data", TASK_ATTEMPT) as metrics):
        raw_dataframe = datalake_service.download_parquet(ec.DATALAKE_BUCKET_NAME, raw_path)
        total_raw_rows = len(raw_dataframe)
        metrics.input_row_count = total_raw_rows
        metrics.source_system = "datalake"
        metrics.source_uri = build_datalake_uri(raw_path)

        cleaned_dataframe = csv_service.clean_data(raw_dataframe)
        total_cleaned_rows = len(cleaned_dataframe)
        metrics.output_row_count = total_cleaned_rows
        metrics.destination_system = "datalake"
        metrics.destination_uri = build_datalake_uri(cleaned_path)

        rejected_row_count = total_raw_rows - total_cleaned_rows
        metrics.rejected_row_count = rejected_row_count

        datalake_service.upload_parquet(cleaned_dataframe, ec.DATALAKE_BUCKET_NAME, cleaned_path)

    publish_written_event(
        source="datalake",
        source_uri=build_datalake_uri(raw_path),
        destination_uri=cleaned_path,
        row_count=total_cleaned_rows,
        layer=DatalakeLayer.CLEANED
    )
    return cleaned_path, total_cleaned_rows, rejected_row_count


def enrich_sale_data(cleaned_path: str, ingestion_time: datetime) -> tuple[str, int]:
    enriched_path = build_sale_datalake_path(DatalakeLayer.ENRICHED, ingestion_time)
    with audit_task_service.audit_task(PIPELINE_NAME, pipeline_id, "enrich_data", TASK_ATTEMPT) as metrics:
        cleaned_dataframe = datalake_service.download_parquet(ec.DATALAKE_BUCKET_NAME, cleaned_path)
        total_cleaned_rows = len(cleaned_dataframe)
        metrics.input_row_count = total_cleaned_rows
        metrics.source_system = "datalake"
        metrics.source_uri = build_datalake_uri(cleaned_path)

        enriched_dataframe = csv_service.enrich_data(cleaned_dataframe)
        total_enriched_rows = len(enriched_dataframe)
        metrics.output_row_count = total_enriched_rows
        metrics.destination_system = "datalake"
        metrics.destination_uri = build_datalake_uri(enriched_path)

        datalake_service.upload_parquet(enriched_dataframe, ec.DATALAKE_BUCKET_NAME, enriched_path)

    publish_written_event(
        source="datalake",
        source_uri=build_datalake_uri(cleaned_path),
        destination_uri=build_datalake_uri(enriched_path),
        row_count=total_enriched_rows,
        layer=DatalakeLayer.ENRICHED
    )
    return enriched_path, total_enriched_rows


def read_enriched_sale_data(enriched_path: str) -> pd.DataFrame:
    with audit_task_service.audit_task(PIPELINE_NAME, pipeline_id, "read_enriched_data", TASK_ATTEMPT) as metrics:
        dataframe = datalake_service.download_parquet(ec.DATALAKE_BUCKET_NAME, enriched_path)
        metrics.input_row_count = metrics.output_row_count = len(dataframe)
        metrics.source_system = "datalake"
        metrics.source_uri = build_datalake_uri(enriched_path)

    publish_read_event(enriched_path, len(dataframe))
    return dataframe


def populate_database(dataframe: pd.DataFrame) -> None:
    with audit_task_service.audit_task(PIPELINE_NAME, pipeline_id, "populate_database", TASK_ATTEMPT) as metrics:
        total_rows = len(dataframe)
        metrics.input_row_count = total_rows
        metrics.output_row_count = total_rows
        metrics.source_system = "dataframe"
        metrics.source_uri = "enriched_dataframe"
        metrics.destination_system = "postgresql"
        metrics.destination_uri = ec.DATABASE_STAGE_TABLE_NAME

        database_service.populate(dataframe)


def populate_datawarehouse(dataframe: pd.DataFrame) -> None:
    with audit_task_service.audit_task(PIPELINE_NAME, pipeline_id, "populate_datawarehouse", TASK_ATTEMPT) as metrics:
        total_rows = len(dataframe)
        metrics.input_row_count = total_rows
        metrics.output_row_count = total_rows
        metrics.source_system = "dataframe"
        metrics.source_uri = "enriched_dataframe"
        metrics.destination_system = "clickhouse"
        metrics.destination_uri = ec.DATAWAREHOUSE_NAME

        datawarehouse_sale_service.populate(dataframe)


def show_data(dataframe: pd.DataFrame) -> None:
    with audit_task_service.audit_task(PIPELINE_NAME, pipeline_id, "show_enriched_sale_data", TASK_ATTEMPT) as metrics:
        total_rows = len(dataframe)
        metrics.input_row_count = total_rows
        metrics.output_row_count = total_rows
        metrics.source_system = "dataframe"
        metrics.source_uri = "enriched_dataframe"
        metrics.destination_system = "Console"
        metrics.destination_uri = "Console"

        show(dataframe)


def process_data_by_csv(dataframe: pd.DataFrame) -> None:
    with audit_task_service.audit_task(PIPELINE_NAME, pipeline_id, "process_data_by_csv", TASK_ATTEMPT) as metrics:
        metrics.input_row_count = len(dataframe)

        revenue_by_category = csv_service.get_revenue_by_category(dataframe)
        revenue_by_country = csv_service.get_revenue_by_country(dataframe)
        metrics.output_row_count = len(revenue_by_category) + len(revenue_by_country)

        show(revenue_by_category)
        show(revenue_by_country)


def process_data_by_datawarehouse() -> None:
    with audit_task_service.audit_task(PIPELINE_NAME, pipeline_id, "process_data_by_datawarehouse",
                                       TASK_ATTEMPT) as metrics:
        revenue_by_category = datawarehouse_sale_service.get_revenue_by_category()
        revenue_by_country = datawarehouse_sale_service.get_revenue_by_country()

        metrics.output_row_count = len(revenue_by_category) + len(revenue_by_country)

        show(revenue_by_category)
        show(revenue_by_country)


def publish_read_event(path: str, row_count: int) -> None:
    producer.publish(
        AuditEvent(
            event_type=AuditEventType.DATASET_READ,
            pipeline_name=PIPELINE_NAME,
            pipeline_id=pipeline_id,
            status=AuditStatus.SUCCEEDED,
            source_system="datalake",
            source_uri=build_datalake_uri(path),
            input_row_count=row_count
        )
    )


def publish_written_event(source: str, source_uri: str, destination_uri: str, row_count: int, layer: str) -> None:
    producer.publish(
        AuditEvent(
            event_type=AuditEventType.DATASET_WRITTEN,
            pipeline_name=PIPELINE_NAME,
            pipeline_id=pipeline_id,
            status=AuditStatus.SUCCEEDED,
            source_system=source,
            source_uri=source_uri,
            destination_system="datalake",
            destination_uri=build_datalake_uri(destination_uri),
            output_row_count=row_count,
            metadata={"datalake_layer": layer}
        )
    )


def flush_producers(*producers: AuditEventProducer) -> None:
    errors = []

    for producer in {id(producer): producer for producer in producers}.values():
        try:
            producer.flush()
        except Exception as error:
            errors.append(error)

    if errors:
        raise errors[0]
