from airflow.exceptions import AirflowException


def ensure_pipeline_success(**context) -> None:
    current_task_id = context["task"].task_id
    failed_tasks = [
        task_instance.task_id
        for task_instance in context["dag_run"].get_task_instances()
        if task_instance.task_id != current_task_id
        and task_instance.state in {"failed", "upstream_failed"}
    ]
    if failed_tasks:
        raise AirflowException(f"Pipeline tasks failed: {', '.join(failed_tasks)}")
