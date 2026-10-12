from data_platform.config.key import Key
from data_platform.model.settings_model import SettingsModel


class TestSettingsModel:

    def test_should_expose_settings_per_connection(self) -> None:
        settings = SettingsModel.from_env({})

        assert settings.app.root
        assert settings.app.resources_dir == "resources"
        assert set(settings.database) == {Key.HOUSE_DATABASE, Key.ONLINE_SHOPPING_DATABASE, Key.AUDIT_DATABASE}
        assert set(settings.data_lake) == {
            Key.PLATFORM_DATA_LAKE,
            Key.HOUSE_DATA_LAKE,
            Key.ONLINE_SHOPPING_DATA_LAKE,
            Key.AUDIT_DATA_LAKE,
        }
        assert set(settings.warehouse) == {Key.HOUSE_WAREHOUSE, Key.ONLINE_SHOPPING_WAREHOUSE, Key.AUDIT_WAREHOUSE}
        assert set(settings.messaging) == {Key.HOUSE_MESSAGING, Key.ONLINE_SHOPPING_MESSAGING, Key.AUDIT_MESSAGING}
        assert settings.data_simulator.url == "http://localhost:8080"
        assert settings.messaging[Key.AUDIT_MESSAGING].channel_name == "audit.audit.events.v1"
        assert settings.data_lake[Key.AUDIT_DATA_LAKE].bucket_name == "audit"

    def test_should_read_each_connection_from_its_own_prefix(self) -> None:
        settings = SettingsModel.from_env({
            "DATA_PLATFORM_HOUSE_DATABASE_HOST": "house-db",
            "DATA_PLATFORM_ONLINE_SHOPPING_DATALAKE_BUCKET_NAME": "shop",
            "DATA_PLATFORM_HOUSE_STREAMING_BOOTSTRAP_SERVERS": "kafka:29092",
        })

        assert settings.database[Key.HOUSE_DATABASE].host == "house-db"
        assert settings.database[Key.HOUSE_DATABASE].jdbc_url == "jdbc:postgresql://house-db:5432/app_database"
        assert settings.database[Key.AUDIT_DATABASE].host == "localhost"
        assert settings.data_lake[Key.ONLINE_SHOPPING_DATA_LAKE].bucket_name == "shop"
        assert settings.messaging[Key.HOUSE_MESSAGING].bootstrap_servers == "kafka:29092"
