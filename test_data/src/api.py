"""REST API over the generated datasets.

Needs the optional ``api`` extra:

    pip install -e .[api]
    python -m api                            # or: uvicorn api:app

Interactive docs are served at ``/docs``, the OpenAPI schema at ``/openapi.json``.
"""


import os
from pathlib import Path

from fastapi import FastAPI, Path as PathParam, Query, Request
from fastapi.responses import FileResponse, JSONResponse

from datasets import Dataset, DatasetRegistry
from exceptions import (
    ConfigurationError,
    CsvGeneratorError,
    DatasetNotFoundError,
    OutputNotFoundError,
    SourceDataError,
)
from schemas import (
    DatasetDetail,
    DatasetSummary,
    ErrorResponse,
    GenerationResponse,
    HealthResponse,
    OutputInfo,
    RowsPage,
)

__version__ = "1.1.0"

#: Environment variable that overrides the folder scanned for ``config_*.json``.
PROJECT_ROOT_ENV = "CSV_GENERATOR_ROOT"

NAME_PARAM = PathParam(description="Dataset name, as in config_<name>.json", examples=["sale"])
NOT_FOUND = {404: {"model": ErrorResponse, "description": "Unknown dataset, or not generated yet"}}
BAD_CONFIG = {400: {"model": ErrorResponse, "description": "Config or source data is not usable"}}


def default_project_root() -> Path:
    """Folder holding the config files: the ``CSV_GENERATOR_ROOT`` env var, or the project root."""
    override = os.environ.get(PROJECT_ROOT_ENV)
    if override:
        return Path(override).resolve()
    return Path(__file__).resolve().parents[1]


def create_app(project_root: Path | None = None) -> FastAPI:
    """Build the FastAPI application for one project folder."""
    registry = DatasetRegistry(project_root or default_project_root())

    app = FastAPI(
        title="CSV Data Generator API",
        version=__version__,
        summary="Generate CSV test datasets and read them back.",
        description=__doc__,
    )
    app.state.registry = registry

    def _relative(path: Path) -> str:
        try:
            return path.relative_to(registry.project_root).as_posix()
        except ValueError:
            return path.as_posix()

    def _output_info(dataset: Dataset) -> OutputInfo:
        status = registry.status(dataset)
        return OutputInfo(
            exists=status.exists,
            file=_relative(status.path),
            size_bytes=status.size_bytes,
            modified_at=status.modified_at,
            row_count=status.row_count,
        )

    def _summary(dataset: Dataset) -> DatasetSummary:
        return DatasetSummary(
            name=dataset.name,
            config_file=_relative(dataset.config_path),
            configured_row_count=dataset.configured_row_count,
            column_count=len(dataset.columns),
            output=_output_info(dataset),
        )

    @app.exception_handler(DatasetNotFoundError)
    @app.exception_handler(OutputNotFoundError)
    async def _not_found(request: Request, error: Exception) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(error)})

    @app.exception_handler(ConfigurationError)
    @app.exception_handler(SourceDataError)
    @app.exception_handler(CsvGeneratorError)
    async def _bad_request(request: Request, error: Exception) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(error)})

    @app.get("/health", response_model=HealthResponse, tags=["meta"])
    async def health() -> HealthResponse:
        """Liveness check, plus how many datasets are visible."""
        return HealthResponse(
            status="ok",
            version=__version__,
            project_root=registry.project_root.as_posix(),
            dataset_count=len(registry.names()),
        )

    @app.get("/datasets", response_model=list[DatasetSummary], tags=["datasets"])
    async def list_datasets() -> list[DatasetSummary]:
        """List every dataset and whether its CSV has been generated."""
        return [_summary(dataset) for dataset in registry.list()]

    @app.get(
        "/datasets/{name}",
        response_model=DatasetDetail,
        tags=["datasets"],
        responses={**NOT_FOUND, **BAD_CONFIG},
    )
    async def get_dataset(name: str = NAME_PARAM) -> DatasetDetail:
        """Read one dataset's configuration and output state."""
        dataset = registry.get(name)
        return DatasetDetail(
            **_summary(dataset).model_dump(),
            columns=list(dataset.columns),
            seed=dataset.config.seed,
        )

    @app.post(
        "/datasets/{name}/generate",
        response_model=GenerationResponse,
        tags=["datasets"],
        responses={**NOT_FOUND, **BAD_CONFIG},
    )
    async def generate_dataset(name: str = NAME_PARAM) -> GenerationResponse:
        """Regenerate a dataset's CSV, replacing any existing file."""
        result = registry.generate(name)
        return GenerationResponse(
            name=name,
            row_count=result.row_count,
            file=_relative(result.output_path),
            download_url=f"/datasets/{name}/download",
        )

    @app.get(
        "/datasets/{name}/rows",
        response_model=RowsPage,
        tags=["files"],
        responses=NOT_FOUND,
    )
    async def read_rows(
        name: str = NAME_PARAM,
        offset: int = Query(0, ge=0, description="Rows to skip"),
        limit: int = Query(100, ge=1, le=1000, description="Rows to return"),
    ) -> RowsPage:
        """Read a page of rows back from the generated CSV as JSON."""
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
        """Download the generated CSV file."""
        path = registry.output_file(name)
        return FileResponse(path, media_type="text/csv", filename=path.name)

    return app


app = create_app()


def run() -> None:
    """Serve the API with uvicorn. Host and port come from ``HOST``/``PORT``."""
    import uvicorn

    uvicorn.run(
        app,
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "8000")),
    )


if __name__ == "__main__":
    run()
