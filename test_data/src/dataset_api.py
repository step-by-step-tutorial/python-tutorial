import os

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse

from dataset_registry import DatasetRegistry
from file_utils import check_file_exists
from dataset_generator import DatasetGenerator
from schemas import DatasetMetadata

__version__ = "1.1.0"


def create_api() -> FastAPI:
    app = FastAPI(
        title="Test Data Generator API",
        version=__version__,
        summary="Generate CSV test datasets and read them back.",
    )

    registry = DatasetRegistry()

    @app.get("/health")
    async def get_health_status() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    @app.get("/datasets")
    async def get_list() -> list[DatasetMetadata]:
        return registry.get_all_metadata()

    @app.get("/datasets/{name}")
    async def get_one(name: str) -> DatasetMetadata:
        return registry.get_one(name).get_metadata()

    @app.post("/datasets/{name}/generate")
    async def generate(name: str) -> DatasetMetadata:
        return DatasetGenerator(config_name=name).write().get_metadata()

    @app.get("/datasets/{name}/download")
    async def download(name: str) -> FileResponse:
        path = registry.get_one(name).output_file
        check_file_exists(path)
        return FileResponse(path, media_type="text/csv", filename=path.name)

    return app


if __name__ == "__main__":
    api = create_api()
    uvicorn.run(
        api,
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8080")),
    )
