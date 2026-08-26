from airflow.exceptions import AirflowException


def ensure_pipeline_success(**context) -> None:
    current_task_id = context["task"].task_id
    dag_run = context["dag_run"]
    if hasattr(dag_run, "get_task_instances"):
        task_states = {
            task_instance.task_id: task_instance.state
            for task_instance in dag_run.get_task_instances()
        }
    else:
        task_instance = context.get("task_instance") or context.get("ti")
        task_states_response = task_instance.get_task_states(
            dag_id=dag_run.dag_id,
            run_ids=[dag_run.run_id],
        )
        task_states = getattr(task_states_response, "task_states", task_states_response)

    failed_tasks = [
        task_id
        for task_id, state in task_states.items()
        if task_id != current_task_id
        and getattr(state, "value", state) in {"failed", "upstream_failed"}
    ]
    if failed_tasks:
        raise AirflowException(f"Pipeline tasks failed: {', '.join(failed_tasks)}")
