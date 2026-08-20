from fastapi import FastAPI

from error_handlers import register_error_handlers
from exceptions import (
    ConfigurationError,
    CsvGeneratorError,
    DatasetNotFoundError,
    OutputNotFoundError,
    SourceDataError,
)


def test_register_error_handlers_installs_expected_handlers() -> None:
    app = FastAPI()

    register_error_handlers(app)

    assert DatasetNotFoundError in app.exception_handlers
    assert OutputNotFoundError in app.exception_handlers
    assert ConfigurationError in app.exception_handlers
    assert SourceDataError in app.exception_handlers
    assert CsvGeneratorError in app.exception_handlers
