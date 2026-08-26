from types import SimpleNamespace

from test_data.writer.writer_registry import WriterRegistry


class RecordingWriter:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.calls = 0

    def write(self, rows, config) -> None:
        self.calls += 1
        if self.error is not None:
            raise self.error


def test_write_all_logs_writer_failure_and_continues(caplog) -> None:
    registry = WriterRegistry()
    failing_writer = RecordingWriter(RuntimeError("database unavailable"))
    succeeding_writer = RecordingWriter()
    registry._writers = {"database": failing_writer, "csv": succeeding_writer}
    config = SimpleNamespace(destinations=("database", "csv"))

    registry.write_all(({"id": "1"},), config)

    assert failing_writer.calls == 1
    assert succeeding_writer.calls == 1
    assert "Writer 'database' failed" in caplog.text
    assert "database unavailable" in caplog.text
    assert "continuing with next writer." in caplog.text


def test_write_all_logs_unknown_writer_and_continues(caplog) -> None:
    registry = WriterRegistry()
    succeeding_writer = RecordingWriter()
    registry._writers = {"csv": succeeding_writer}
    config = SimpleNamespace(destinations=("missing", "csv"))

    registry.write_all((), config)

    assert succeeding_writer.calls == 1
    assert "Writer 'missing' is not registered; continuing with next writer." in caplog.text
