from pydantic import BaseModel


class DatabasePageModel(BaseModel):
    page: int
    page_size: int
    total: int
    items: list[dict[str, str | None]]
