INSERT INTO audit.task (
    task_id,
    pipeline_id,
    task_name,
    task_attempt,
    started_at,
    status
)
VALUES (
    :task_id,
    :pipeline_id,
    :task_name,
    :task_attempt,
    :started_at,
    :status
)
ON CONFLICT (task_id) DO NOTHING;