UPDATE audit.pipeline
SET completed_at = :completed_at,
    status = :status,
    input_row_count = :input_row_count,
    output_row_count = :output_row_count,
    rejected_row_count = :rejected_row_count,
    duration_ms = :duration_ms,
    error_message = :error_message,
    updated_at = CURRENT_TIMESTAMP
WHERE pipeline_id = :pipeline_id;
