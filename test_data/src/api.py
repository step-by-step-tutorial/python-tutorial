import os

from fastapi import FastAPI, Path as PathParam, Query
from fastapi.responses import FileResponse

import env_config
from datasets import DatasetRegistry
from file_utils import list_of_file_names
from mapper import DatasetMapper
from error_handlers import register_error_handlers
from env_config import PROJECT_ROOT
from schemas import (
    DatasetDetail,
    DatasetSummary,
    ErrorResponse,
    GenerationResponse,
    HealthResponse,
    RowsPage,
)

__version__ = "1.1.0"

NAME_PARAM = PathParam(description="Config file name, for example sale.json", examples=["sale.json"])
NOT_FOUND = {404: {"model": ErrorResponse, "description": "Unknown dataset, or not generated yet"}}
BAD_CONFIG = {400: {"model": ErrorResponse, "description": "Config or source data is not usable"}}


def create_app() -> FastAPI:
    registry = DatasetRegistry()
    mapper = DatasetMapper(registry)

    app = FastAPI(
        title="CSV Data Generator API",
        version=__version__,
        summary="Generate CSV test datasets and read them back.",
        description=__doc__,
    )
    app.state.registry = registry
    register_error_handlers(app)

    @app.get("/health", response_model=HealthResponse, tags=["meta"])
    async def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            version=__version__,
            project_root=PROJECT_ROOT.as_posix(),
            dataset_count=len(list_of_file_names(env_config.CONFIG_DIR)),
        )

    @app.get("/datasets", response_model=list[DatasetSummary], tags=["datasets"])
    async def list_datasets() -> list[DatasetSummary]:
        return [mapper.summary(dataset) for dataset in registry.list()]

    @app.get("/datasets/{name}", response_model=DatasetDetail, tags=["datasets"], responses={**NOT_FOUND, **BAD_CONFIG})
    async def get_dataset(name: str = NAME_PARAM) -> DatasetDetail:
        dataset = registry.get(name)
        return DatasetDetail(
            **mapper.summary(dataset).model_dump(),
            columns=list(dataset.columns),
            seed=dataset.config.seed,
        )

    @app.post("/datasets/{name}/generate", response_model=GenerationResponse, tags=["datasets"],
              responses={**NOT_FOUND, **BAD_CONFIG})
    async def generate_dataset(name: str = NAME_PARAM) -> GenerationResponse:
        result = registry.generate(name)
        return GenerationResponse(
            name=name,
            row_count=result.row_count,
            file=mapper.relative(result.output_path),
            download_url=f"/datasets/{name}/download",
        )

    @app.get("/datasets/{name}/rows", response_model=RowsPage, tags=["files"], responses=NOT_FOUND)
    async def read_rows(
            name: str = NAME_PARAM,
            offset: int = Query(0, ge=0, description="Rows to skip"),
            limit: int = Query(100, ge=1, le=1000, description="Rows to return"),
    ) -> RowsPage:
        rows = registry.read_rows(name, offset=offset, limit=limit)
        status = registry.status(registry.get(name))
        return RowsPage(
            name=name,
            offset=offset,
            limit=limit,
            returned=len(rows),
            total=status.row_count or 0,
            rows=rows,
        )

    @app.get(
        "/datasets/{name}/download",
        tags=["files"],
        response_class=FileResponse,
        responses={**NOT_FOUND, 200: {"content": {"text/csv": {}}, "description": "The CSV file"}},
    )
    async def download(name: str = NAME_PARAM) -> FileResponse:
        path = registry.output_file(name)
        return FileResponse(path, media_type="text/csv", filename=path.name)

    return app


def run() -> None:
    import uvicorn

    app = create_app()
    uvicorn.run(
        app,
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "8080")),
    )


if __name__ == "__main__":
    run()
