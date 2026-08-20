import os

from fastapi import FastAPI, Path as PathParam
from fastapi.responses import FileResponse

import env_config
from datasets import DatasetRegistry
from env_config import PROJECT_ROOT
from error_handlers import register_error_handlers
from file_utils import list_of_file_names, output_file_path
from exceptions import OutputNotFoundError
from generator import generate_dataset as run_generation
from schemas import (
    DatasetDetail,
    DatasetSummary,
    ErrorResponse,
    HealthResponse,
)

__version__ = "1.1.0"

NAME_PARAM = PathParam(description="Config file name, for example sale.json", examples=["sale.json"])
NOT_FOUND = {404: {"model": ErrorResponse, "description": "Unknown dataset, or not generated yet"}}
BAD_CONFIG = {400: {"model": ErrorResponse, "description": "Config or source data is not usable"}}


def create_app() -> FastAPI:
    registry = DatasetRegistry()

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
        return [dataset.to_summary() for dataset in registry.list()]

    @app.get("/datasets/{name}", response_model=DatasetDetail, tags=["datasets"], responses={**NOT_FOUND, **BAD_CONFIG})
    async def get_dataset(name: str = NAME_PARAM) -> DatasetDetail:
        dataset = registry.get(name)
        return DatasetDetail(
            **dataset.to_summary().model_dump(),
            columns=list(dataset.columns),
            seed=dataset.config.seed,
        )

    @app.post("/datasets/{name}/generate", response_model=DatasetSummary, tags=["datasets"],
              responses={**NOT_FOUND, **BAD_CONFIG})
    async def generate_dataset(name: str = NAME_PARAM) -> DatasetSummary:
        run_generation(env_config.CONFIG_DIR / name)
        return registry.get(name).to_summary()

    @app.get(
        "/datasets/{name}/download",
        tags=["files"],
        response_class=FileResponse,
        responses={**NOT_FOUND, 200: {"content": {"text/csv": {}}, "description": "The CSV file"}},
    )
    async def download(name: str = NAME_PARAM) -> FileResponse:
        dataset = registry.get(name)
        path = output_file_path(dataset.config.output_file)
        if not path.is_file():
            raise OutputNotFoundError(
                f"Dataset {name!r} has not been generated yet. "
                f"POST /datasets/{name}/generate first."
            )
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
