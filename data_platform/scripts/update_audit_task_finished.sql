UPDATE audit.task
SET completed_at = :completed_at,
    status = :status,
    input_row_count = :input_row_count,
    output_row_count = :output_row_count,
    rejected_row_count = :rejected_row_count,
    duration_ms = :duration_ms,
    error_type = :error_type,
    error_message = :error_message
WHERE task_id = :task_id;
