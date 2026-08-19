from connector import registry as system_under_test


class TestConnectionRegistry:

    def test_should_cache_connections_until_closed(self) -> None:
        created: list[object] = []

        def create_connection() -> object:
            connection = object()
            created.append(connection)
            return connection

        connection_name = "test.connection.cache"
        system_under_test.registry.pop(connection_name, None)
        system_under_test.factories[connection_name] = create_connection

        first = system_under_test.get_connection(connection_name)
        second = system_under_test.get_connection(connection_name)

        assert first is second
        assert created == [first]

        system_under_test.close_connection(connection_name)
        assert connection_name not in system_under_test.registry

    def test_should_flush_before_close_when_available(self) -> None:
        calls: list[str] = []

        class DummyConnection:
            def flush(self) -> None:
                calls.append("flush")

            def close(self) -> None:
                calls.append("close")

        connection_name = "test.connection.cleanup"
        system_under_test.registry.pop(connection_name, None)
        system_under_test.registry[connection_name] = DummyConnection()

        _ = system_under_test.get_connection(connection_name)
        system_under_test.close_connection(connection_name)

        assert calls == ["flush", "close"]
        assert connection_name not in system_under_test.registry
