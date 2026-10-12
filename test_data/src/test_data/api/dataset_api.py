import logging
import os

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from sqlalchemy.exc import NoSuchTableError

from test_data.repository.database_repository import DatabaseRepository
from test_data.generator.dataset_generator import DatasetGenerator
from test_data.model.database_page_model import DatabasePageModel
from test_data.model.dataset_metadata_model import DatasetMetadataModel
from test_data.model.settings_model import SettingsModel
from test_data.repository.dataset_repository import DatasetNotFoundError, DatasetRepository
from test_data.util.file_utils import check_file_exists
from test_data.writer.writer_registry import WriterError

__version__ = "1.1.0"
MEDIA_TYPES = {"csv": "text/csv", "json": "application/json", "xml": "application/xml"}
logger = logging.getLogger(__name__)


def create_api(settings: SettingsModel | None = None) -> FastAPI:
    settings = settings or SettingsModel.from_env()
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

    datasets = DatasetRepository(settings)
    database = DatabaseRepository(settings.database_url, schema=settings.database_schema)
    logger.info("Data simulator API initialized: datasets=%s", datasets.get_all_names())

    @app.exception_handler(DatasetNotFoundError)
    async def handle_dataset_not_found(request: Request, error: DatasetNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(error)})

    @app.exception_handler(WriterError)
    async def handle_writer_error(request: Request, error: WriterError) -> JSONResponse:
        return JSONResponse(status_code=500, content={"detail": str(error), "failures": error.failures})

    @app.get("/", include_in_schema=False)
    async def redirect_to_health() -> RedirectResponse:
        return RedirectResponse(url="/health")

    @app.get("/health", tags=["Health"], summary="Get service health")
    async def get_health_status() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    @app.get("/datasets", tags=["Datasets"], summary="List datasets")
    async def get_list() -> list[DatasetMetadataModel]:
        return datasets.get_all_metadata()

    @app.get("/datasets/names", tags=["Datasets"], summary="List dataset names")
    async def get_names() -> list[str]:
        return datasets.get_all_names()

    @app.get("/datasets/{name}", tags=["Datasets"], summary="Get dataset metadata")
    async def get_one(name: str) -> DatasetMetadataModel:
        return DatasetMetadataModel.from_config(datasets.get_one(name), settings)

    @app.post("/datasets/{name}/generate", tags=["Datasets"], summary="Generate dataset output")
    async def generate(name: str) -> DatasetMetadataModel:
        logger.info("Dataset generation requested: dataset=%s", name)
        config = DatasetGenerator(datasets.get_one(name).name, settings).write()
        return DatasetMetadataModel.from_config(config, settings)

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
    ) -> DatabasePageModel:
        logger.info("Dataset rows requested: dataset=%s page=%s page_size=%s", name, page, page_size)
        config = datasets.get_one(name)
        if "database" not in config.destinations:
            raise HTTPException(status_code=404, detail=f"Dataset {name} has no database destination.")

        try:
            items, total = database.read_page(
                table_name=config.table_name,
                page=page,
                page_size=page_size,
            )
        except NoSuchTableError as error:
            raise HTTPException(status_code=404, detail=f"Database table for {name} was not found.") from error

        logger.info("Dataset rows returned: dataset=%s page=%s returned=%s total=%s", name, page, len(items), total)
        return DatabasePageModel(page=page, page_size=page_size, total=total, items=items)

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
        logger.info("Dataset download requested: dataset=%s format=%s", name, format_name)
        config = datasets.get_one(name)
        if format_name not in config.destinations:
            raise HTTPException(status_code=404, detail=f"Format '{format_name}' is not available for {name}.")

        media_type = MEDIA_TYPES.get(format_name)
        if media_type is None:
            raise HTTPException(status_code=404, detail=f"Unsupported format: {format_name}.")

        path = config.output_file(format_name)

        try:
            check_file_exists(path)
        except FileNotFoundError as error:
            raise HTTPException(status_code=404, detail=f"Output for {name} has not been generated yet.") from error
        logger.info("Dataset download ready: dataset=%s format=%s path=%s bytes=%s",
                    name, format_name, path, path.stat().st_size)
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
