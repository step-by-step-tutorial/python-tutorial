from types import SimpleNamespace

import pytest

from test_data_platform.model.settings_model import SettingsModel
from test_data_platform.writer.writer_registry import WriterError, WriterRegistry


class RecordingWriter:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.calls = 0

    def write(self, rows, config) -> None:
        self.calls += 1
        if self.error is not None:
            raise self.error


def test_write_all_logs_writer_failure_and_continues(caplog) -> None:
    registry = WriterRegistry(SettingsModel.from_env({}))
    failing_writer = RecordingWriter(RuntimeError("database unavailable"))
    succeeding_writer = RecordingWriter()
    registry._writers = {"database": failing_writer, "csv": succeeding_writer}
    config = SimpleNamespace(name="demo.json", destinations=("database", "csv"))

    with pytest.raises(WriterError) as error:
        registry.write_all(({"id": "1"},), config)

    assert error.value.failures == {"database": "database unavailable"}
    assert failing_writer.calls == 1
    assert succeeding_writer.calls == 1
    assert "Writer 'database' failed" in caplog.text
    assert "database unavailable" in caplog.text
    assert "continuing with next writer." in caplog.text


def test_write_all_logs_unknown_writer_and_continues(caplog) -> None:
    registry = WriterRegistry(SettingsModel.from_env({}))
    succeeding_writer = RecordingWriter()
    registry._writers = {"csv": succeeding_writer}
    config = SimpleNamespace(name="demo.json", destinations=("missing", "csv"))

    with pytest.raises(WriterError, match="missing"):
        registry.write_all((), config)

    assert succeeding_writer.calls == 1
    assert "Writer 'missing' is not registered; continuing with next writer." in caplog.text


def test_write_all_succeeds_when_all_writers_succeed() -> None:
    registry = WriterRegistry(SettingsModel.from_env({}))
    writer = RecordingWriter()
    registry._writers = {"csv": writer}

    registry.write_all(({"id": "1"},), SimpleNamespace(name="demo.json", destinations=("csv",)))

    assert writer.calls == 1
