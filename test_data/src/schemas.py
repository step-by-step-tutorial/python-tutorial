from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(examples=["ok"])
    version: str
    project_root: str
    dataset_count: int

class DatasetSummary(BaseModel):
    name: str
    config_file: str
    row_count: int
    column_count: int
    destinations: list[str]
    file: str = Field(description="Path relative to the project root")
    download_url: str


class DatasetDetail(DatasetSummary):
    columns: list[str]
    seed: int | None = None


class ErrorResponse(BaseModel):
    detail: str
