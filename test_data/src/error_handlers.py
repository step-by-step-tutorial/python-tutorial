from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from exceptions import (
    ConfigurationError,
    CsvGeneratorError,
    DatasetNotFoundError,
    OutputNotFoundError,
    SourceDataError,
)


async def _json_error(request: Request, error: Exception, status_code: int) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": str(error)})


def _handler(status_code: int):
    async def handler(request: Request, error: Exception) -> JSONResponse:
        return _json_error(request, error, status_code)

    return handler


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DatasetNotFoundError, _handler(404))
    app.add_exception_handler(OutputNotFoundError, _handler(404))
    app.add_exception_handler(ConfigurationError, _handler(400))
    app.add_exception_handler(SourceDataError, _handler(400))
    app.add_exception_handler(CsvGeneratorError, _handler(400))
