from pydantic import BaseModel, Field


class DatasetMetadata(BaseModel):
    name: str
    config_file: str
    row_count: int
    column_count: int
    columns: list[str]
    destinations: list[str]
    file: str = Field(description="Path relative to the project root")
    download_url: str