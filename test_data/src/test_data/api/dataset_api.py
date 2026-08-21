import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.exc import NoSuchTableError

from test_data.config import settings as env_config
from test_data.repository.database_repository import DatabaseRepository
from test_data.generator.dataset_generator import DatasetGenerator
from test_data.generator.dataset_registry import DatasetRegistry
from test_data.model.schemas import DatabasePage, DatasetMetadata
from test_data.util.file_utils import check_file_exists
from test_data.util.output_format_utils import media_type_for

__version__ = "1.1.0"


def create_api() -> FastAPI:
    app = FastAPI(
        title="Test Data Generator API",
        version=__version__,
        summary="Generate test datasets and download configured output formats.",
        description="Generate datasets from JSON configurations and download their CSV, JSON, or XML output.",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        openapi_tags=[
            {"name": "Health", "description": "Service health and version information."},
            {"name": "Datasets", "description": "Discover, generate, and download datasets."},
        ],
    )

    registry = DatasetRegistry()

    @app.get("/", include_in_schema=False)
    async def redirect_to_health() -> RedirectResponse:
        return RedirectResponse(url="/health")

    @app.get("/health", tags=["Health"], summary="Get service health")
    async def get_health_status() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    @app.get("/datasets", tags=["Datasets"], summary="List datasets")
    async def get_list() -> list[DatasetMetadata]:
        return registry.get_all_metadata()

    @app.get("/datasets/names", tags=["Datasets"], summary="List dataset names")
    async def get_names() -> list[str]:
        return registry.get_all_names()

    @app.get("/datasets/{name}", tags=["Datasets"], summary="Get dataset metadata")
    async def get_one(name: str) -> DatasetMetadata:
        return registry.get_one(name).get_metadata()

    @app.post("/datasets/{name}/generate", tags=["Datasets"], summary="Generate dataset output")
    async def generate(name: str) -> DatasetMetadata:
        return DatasetGenerator(config_name=name).write().get_metadata()

    @app.get(
        "/datasets/{name}/rows",
        tags=["Datasets"],
        summary="Read paginated database rows",
        response_description="One page of rows from the generated dataset table.",
        responses={404: {"description": "Dataset is not database-backed or its table was not found."}},
    )
    async def get_rows(
            name: str,
            page: int = Query(1, ge=1, description="One-based page number."),
            page_size: int = Query(100, ge=1, le=1_000, description="Maximum number of rows to return."),
    ) -> DatabasePage:
        dataset = registry.get_one(name)
        if "database" not in dataset.destinations:
            raise HTTPException(status_code=404, detail=f"Dataset {name} has no database destination.")

        try:
            items, total = DatabaseRepository(env_config.DATABASE_URL).read_page(
                table_name=Path(dataset.config.output_name).stem,
                page=page,
                page_size=page_size,
            )
        except NoSuchTableError as error:
            raise HTTPException(status_code=404, detail=f"Database table for {name} was not found.") from error

        return DatabasePage(page=page, page_size=page_size, total=total, items=items)

    @app.get(
        "/datasets/{name}/download",
        tags=["Datasets"],
        summary="Download generated output",
        response_description="The generated dataset file in the requested format.",
        responses={404: {"description": "Dataset, format, or generated output file was not found."}},
    )
    async def download(
            name: str,
            format_name: str = Query(
                "csv",
                alias="format",
                description="Configured output format to download, such as csv, json, or xml.",
            ),
    ) -> FileResponse:
        dataset = registry.get_one(name)
        if format_name not in dataset.destinations:
            raise HTTPException(status_code=404, detail=f"Format '{format_name}' is not available for {name}.")

        try:
            path = dataset.output_file_for(format_name)
            media_type = media_type_for(format_name)
        except KeyError as error:
            raise HTTPException(status_code=404, detail=f"Unsupported format: {format_name}.") from error

        check_file_exists(path)
        return FileResponse(path, media_type=media_type, filename=path.name)

    return app


def run() -> None:
    api = create_api()
    uvicorn.run(
        api,
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8080")),
    )


if __name__ == "__main__":
    run()
