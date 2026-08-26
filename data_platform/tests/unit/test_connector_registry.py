from data_platform.registry.connection_registry import connection_registry


class TestConnectionRegistry:

    def test_should_cache_connections_until_closed(self) -> None:
        created: list[object] = []

        def create_connection() -> object:
            connection = object()
            created.append(connection)
            return connection

        connection_name = "test.connection.cache"
        connection_registry.remove(connection_name)
        connection_registry.register_lazy_item(connection_name, create_connection)

        first = connection_registry.get_item(connection_name)
        second = connection_registry.get_item(connection_name)

        assert first is second
        assert created == [first]

        connection_registry.close(connection_name)
        third = connection_registry.get_item(connection_name)

        assert third is not first
        assert created == [first, third]

        connection_registry.close(connection_name)

    def test_should_flush_before_close_when_available(self) -> None:
        calls: list[str] = []

        class DummyConnection:
            def flush(self) -> None:
                calls.append("flush")

            def close(self) -> None:
                calls.append("close")

        connection_name = "test.connection.cleanup"
        connection_registry.remove(connection_name)
        connection_registry.register(connection_name, DummyConnection())

        _ = connection_registry.get_item(connection_name)
        connection_registry.close(connection_name)

        assert calls == ["flush", "close"]
        assert not connection_registry.contains(connection_name)


