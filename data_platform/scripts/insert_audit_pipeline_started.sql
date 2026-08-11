INSERT INTO audit.pipeline (
    pipeline_id,
    pipeline_name,
    airflow_dag_id,
    airflow_dag_run_id,
    logical_date,
    started_at,
    status
)
VALUES (
    :pipeline_id,
    :pipeline_name,
    :airflow_dag_id,
    :airflow_dag_run_id,
    :logical_date,
    :started_at,
    :status
)
ON CONFLICT (pipeline_id)
DO UPDATE
    SET
        status = EXCLUDED.status,
        updated_at = CURRENT_TIMESTAMP;