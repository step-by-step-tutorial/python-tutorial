import json
import importlib
from pathlib import Path

from fastapi.testclient import TestClient

import env_config
from dataset_api import create_api
from dataset_generator import DatasetGenerator


def test_download_serves_requested_output_format(project_root: Path) -> None:
    config_path = env_config.CONFIG_DIR / "demo.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["destinations"] = ["csv", "json", "xml"]
    config_path.write_text(json.dumps(config), encoding="utf-8")
    DatasetGenerator("demo.json").write()

    client = TestClient(create_api())

    csv_response = client.get("/datasets/demo.json/download?format=csv")
    json_response = client.get("/datasets/demo.json/download?format=json")
    xml_response = client.get("/datasets/demo.json/download?format=xml")

    assert csv_response.status_code == 200
    assert csv_response.headers["content-type"] == "text/csv; charset=utf-8"
    assert csv_response.headers["content-disposition"] == 'attachment; filename="demo.csv"'
    assert json_response.status_code == 200
    assert json_response.headers["content-type"] == "application/json"
    assert json_response.json()[0]["order_id"] == "1"
    assert xml_response.status_code == 200
    assert xml_response.headers["content-type"] == "application/xml"
    assert b"<order_id>1</order_id>" in xml_response.content


def test_download_rejects_unconfigured_format(project_root: Path) -> None:
    response = TestClient(create_api()).get("/datasets/demo.json/download?format=json")

    assert response.status_code == 404


def test_openapi_documentation_describes_dataset_routes(project_root: Path) -> None:
    client = TestClient(create_api())
    schema = client.get("/openapi.json").json()

    assert client.get("/docs").status_code == 200
    assert client.get("/redoc").status_code == 200
    assert schema["info"]["title"] == "Test Data Generator API"
    assert "/datasets/{name}/download" in schema["paths"]
    assert schema["paths"]["/datasets/{name}/download"]["get"]["tags"] == ["Datasets"]


def test_root_redirects_to_health(project_root: Path) -> None:
    response = TestClient(create_api()).get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/health"


def test_get_rows_reads_a_database_page(project_root: Path, monkeypatch) -> None:
    config_path = env_config.CONFIG_DIR / "demo.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["destinations"] = ["database"]
    config_path.write_text(json.dumps(config), encoding="utf-8")
    database_path = project_root / "test_data.sqlite"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+pysqlite:///{database_path}")
    importlib.reload(env_config)
    try:
        DatasetGenerator("demo.json").write()

        response = TestClient(create_api()).get("/datasets/demo.json/rows?page=2&page_size=2")

        assert response.status_code == 200
        assert response.json()["page"] == 2
        assert response.json()["page_size"] == 2
        assert response.json()["total"] == 5
        assert len(response.json()["items"]) == 2
    finally:
        monkeypatch.delenv("DATABASE_URL", raising=False)
        importlib.reload(env_config)
