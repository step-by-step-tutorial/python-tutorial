import builtins
import importlib
import sys

import pytest

pytestmark = pytest.mark.unit


class TestLazyImports:

    def test_main_import_should_not_touch_spark_or_clickhouse(self, mocker) -> None:
        original_import = builtins.__import__

        def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name in {"clickhouse_connect", "pyspark"}:
                raise AssertionError(f"{name} should not be imported")
            return original_import(name, globals, locals, fromlist, level)

        for module_name in list(sys.modules):
            if module_name == "main" or module_name.startswith("pipeline") or module_name.startswith("service.spark"):
                sys.modules.pop(module_name, None)

        mocker.patch("builtins.__import__", side_effect=guarded_import)

        module = importlib.import_module("main")

        assert module.run_pipeline is not None

    def test_service_spark_runtime_import_should_not_touch_pyspark(self, mocker) -> None:
        original_import = builtins.__import__

        def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "pyspark":
                raise AssertionError("pyspark should not be imported")
            return original_import(name, globals, locals, fromlist, level)

        for module_name in list(sys.modules):
            if module_name.startswith("service.spark"):
                sys.modules.pop(module_name, None)

        mocker.patch("builtins.__import__", side_effect=guarded_import)

        module = importlib.import_module("service.spark.runtime")

        assert module.persisted_dataframes is not None
