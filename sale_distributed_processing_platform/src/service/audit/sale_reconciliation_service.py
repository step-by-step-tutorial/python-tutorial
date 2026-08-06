from model.audit_event import AuditEvent, AuditEventType, AuditStatus
from model.audit_metrics import SaleReconciliationMetrics
from streaming.audit_event_producer import publish


class SaleReconciliationError(ValueError):
    pass


def reconcile(
        producer,
        pipeline_name: str,
        pipeline_id: str,
        task_name: str,
        metrics: SaleReconciliationMetrics,
) -> None:
    kafka_matches_bronze = metrics.kafka_consumed_count == metrics.bronze_row_count
    bronze_matches_processed = metrics.bronze_row_count == metrics.silver_row_count + metrics.rejected_row_count
    silver_matches_database = metrics.silver_row_count == metrics.database_written_count
    is_reconciled = kafka_matches_bronze and bronze_matches_processed and silver_matches_database
    status = AuditStatus.SUCCEEDED if is_reconciled else AuditStatus.FAILED

    publish(
        producer,
        AuditEvent(
            event_type=AuditEventType.RECONCILIATION_COMPLETED,
            pipeline_name=pipeline_name,
            pipeline_id=pipeline_id,
            task_name=task_name,
            status=status,
            input_row_count=metrics.kafka_consumed_count,
            output_row_count=metrics.database_written_count,
            rejected_row_count=metrics.rejected_row_count,
            metadata={
                "kafka_consumed_count": metrics.kafka_consumed_count,
                "bronze_row_count": metrics.bronze_row_count,
                "silver_row_count": metrics.silver_row_count,
                "rejected_row_count": metrics.rejected_row_count,
                "database_written_count": metrics.database_written_count,
                "kafka_matches_bronze": kafka_matches_bronze,
                "bronze_matches_processed": bronze_matches_processed,
                "silver_matches_database": silver_matches_database,
                "is_reconciled": is_reconciled,
            },
        )
    )

    if not is_reconciled:
        raise SaleReconciliationError("Sale pipeline reconciliation failed.")
