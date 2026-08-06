from uuid import uuid4


def create_pipeline_id() -> str:
    return str(uuid4())
