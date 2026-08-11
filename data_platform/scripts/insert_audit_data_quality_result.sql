INSERT INTO audit.data_quality_result (
    data_quality_result_id,
    pipeline_id,
    task_id,
    dataset_name,
    check_name,
    check_type,
    status,
    expected_value,
    actual_value,
    failed_row_count,
    sample_failure_uri,
    checked_at,
    metadata
) VALUES (
    :data_quality_result_id,
    :pipeline_id,
    :task_id,
    :dataset_name,
    :check_name,
    :check_type,
    :status,
    :expected_value,
    :actual_value,
    :failed_row_count,
    :sample_failure_uri,
    :checked_at,
    CAST(:metadata AS JSONB)
)
ON CONFLICT (data_quality_result_id) DO NOTHING;