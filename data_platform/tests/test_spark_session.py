from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile

import pytest

from connector.spark import session as system_under_test

pytestmark = pytest.mark.unit


class TestSourceArchive:

    def test_should_build_a_source_archive_with_project_packages(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.setattr(system_under_test.tempfile, "gettempdir", lambda: str(tmp_path))
        system_under_test._build_source_archive.cache_clear()

        archive_path = Path(system_under_test._build_source_archive())

        assert archive_path.exists()
        with ZipFile(archive_path) as archive:
            names = set(archive.namelist())

        assert "dataset/definition.py" in names
        assert "persistence/datawarehouse/writer.py" in names

    def test_should_register_the_source_archive_with_spark(self, mocker, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.setattr(system_under_test.tempfile, "gettempdir", lambda: str(tmp_path))
        system_under_test._build_source_archive.cache_clear()

        given_session = mocker.Mock()
        builder = mocker.Mock()
        builder.appName.return_value = builder
        builder.master.return_value = builder
        builder.config.return_value = builder
        builder.getOrCreate.return_value = given_session

        mocker.patch.object(system_under_test.SparkSession, "builder", builder)

        system_under_test.create_session()

        assert given_session.sparkContext.addPyFile.call_count == 1
        archive_path = Path(given_session.sparkContext.addPyFile.call_args.args[0])
        assert archive_path.exists()
