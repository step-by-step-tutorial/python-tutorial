import builtins
import importlib
import sys

import pytest

pytestmark = pytest.mark.unit


class TestLazyImports:

    def test_inmemory_pipeline_import_should_not_touch_clickhouse_client(self, mocker) -> None:
        original_import = builtins.__import__

        def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "clickhouse_connect":
                raise AssertionError("clickhouse_connect should not be imported")
            return original_import(name, globals, locals, fromlist, level)

        for module_name in list(sys.modules):
            if module_name.startswith("pipeline") or module_name.startswith("persistence.datawarehouse") or module_name.startswith("connector.datawarehouse"):
                sys.modules.pop(module_name, None)

        mocker.patch("builtins.__import__", side_effect=guarded_import)

        module = importlib.import_module("pipeline.inmemory_pipeline")

        assert module.InmemoryPipeline is not None
