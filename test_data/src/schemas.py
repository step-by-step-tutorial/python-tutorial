

from datetime import datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):

    status: str = Field(examples=["ok"])
    version: str
    project_root: str
    dataset_count: int


class OutputInfo(BaseModel):

    exists: bool
    file: str = Field(description="Path relative to the project root")
    size_bytes: int | None = None
    modified_at: datetime | None = None
    row_count: int | None = Field(default=None, description="Data rows in the file, header excluded")


class DatasetSummary(BaseModel):

    name: str
    config_file: str
    configured_row_count: int
    column_count: int
    destinations: list[str]
    output: OutputInfo


class DatasetDetail(DatasetSummary):

    columns: list[str]
    seed: int | None = None


class GenerationResponse(BaseModel):

    name: str
    row_count: int
    file: str
    download_url: str


class RowsPage(BaseModel):

    name: str
    offset: int
    limit: int
    returned: int
    total: int
    rows: list[dict[str, str]]


class ErrorResponse(BaseModel):

    detail: str
