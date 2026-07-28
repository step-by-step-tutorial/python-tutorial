"""Request and response models for the REST API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Service liveness."""

    status: str = Field(examples=["ok"])
    version: str
    project_root: str
    dataset_count: int


class OutputInfo(BaseModel):
    """State of a dataset's CSV file."""

    exists: bool
    file: str = Field(description="Path relative to the project root")
    size_bytes: int | None = None
    modified_at: datetime | None = None
    row_count: int | None = Field(default=None, description="Data rows in the file, header excluded")


class DatasetSummary(BaseModel):
    """One dataset, as listed by ``GET /datasets``."""

    name: str
    config_file: str
    configured_row_count: int
    column_count: int
    output: OutputInfo


class DatasetDetail(DatasetSummary):
    """One dataset, including its column names and seed."""

    columns: list[str]
    seed: int | None = None


class GenerationResponse(BaseModel):
    """Result of a generation run."""

    name: str
    row_count: int
    file: str
    download_url: str


class RowsPage(BaseModel):
    """A page of rows read back from a generated CSV."""

    name: str
    offset: int
    limit: int
    returned: int
    total: int
    rows: list[dict[str, str]]


class ErrorResponse(BaseModel):
    """Any 4xx response body."""

    detail: str
