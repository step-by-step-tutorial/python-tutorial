from collections.abc import Iterable

from model.audit_event import AuditEvent, AuditEventType, AuditStatus
from model.data_quality_result import DataQualityResult, SaleDataQualityStatus
from repository.audit_repository import save_data_quality_result

class QualityService:
    def __init__(self, producer):
        self.producer = producer

    def check_required_fields(
            self,
            pipeline_name: str,
            pipeline_id: str,
            task_id: str,
            dataset_name: str,
            rows: Iterable[dict],
            required_fields: list[str],
    ) -> DataQualityResult:
        materialized_rows = list(rows)
        failed_row_count = sum(
            1
            for row in materialized_rows
            if any(row.get(required_field) is None for required_field in required_fields)
        )
        quality_status = SaleDataQualityStatus.PASSED if failed_row_count == 0 else SaleDataQualityStatus.FAILED

        result = DataQualityResult(
            pipeline_id=pipeline_id,
            task_id=task_id,
            dataset_name=dataset_name,
            check_name="required_fields",
            check_type="NOT_NULL",
            status=quality_status,
            expected_value="0",
            actual_value=str(failed_row_count),
            failed_row_count=failed_row_count,
            metadata={"required_fields": required_fields},
        )

        save_data_quality_result(engine, result)

        self.producer.publish(
            AuditEvent(
                event_type=AuditEventType.DATA_QUALITY_CHECKED,
                pipeline_name=pipeline_name,
                pipeline_id=pipeline_id,
                task_name="check_sale_data_quality",
                task_id=task_id,
                status=AuditStatus.SUCCEEDED if failed_row_count == 0 else AuditStatus.FAILED,
                input_row_count=len(materialized_rows),
                rejected_row_count=failed_row_count,
                metadata=result.model_dump(mode="json"),
            )
        )

        return result
