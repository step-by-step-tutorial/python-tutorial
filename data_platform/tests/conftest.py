from __future__ import annotations

import pytest


def pytest_collection_modifyitems(session, config, items):
    for item in items:
        path = str(item.path).lower()
        tagged = False
        if "spark" in path:
            item.add_marker(pytest.mark.spark)
            tagged = True
        if "kafka" in path or "streaming" in path:
            item.add_marker(pytest.mark.kafka)
            tagged = True
        if "database" in path:
            item.add_marker(pytest.mark.database)
            tagged = True
        if "datawarehouse" in path:
            item.add_marker(pytest.mark.datawarehouse)
            tagged = True
        if "integration" in path:
            item.add_marker(pytest.mark.integration)
            tagged = True
        elif "e2e" in path:
            item.add_marker(pytest.mark.e2e)
            tagged = True
        if not tagged:
            item.add_marker(pytest.mark.unit)
