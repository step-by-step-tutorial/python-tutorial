from data_platform.config.main_settings import settings


class TestMainSettings:

    def test_should_expose_mapped_settings(self) -> None:
        assert settings.app.root
        assert settings.app.resources_dir == "resources"
        assert set(settings.database) == {"data-platform.database", "house.database", "online_shopping.database", "audit.database"}
        assert set(settings.data_lake) == {
            "data-platform.datalake",
            "data-platform.backup.datalake",
            "house.datalake",
            "house.backup.datalake",
            "audit.datalake",
        }
        assert set(settings.warehouse) == {"data-platform.warehouse", "house.warehouse", "online_shopping.warehouse", "audit.warehouse"}
        assert set(settings.messaging) == {
            "house.kafka.listener",
            "house.kafka.producer",
            "online_shopping.kafka.listener",
            "audit.kafka.producer",
            "audit.kafka.listener",
        }
        assert settings.api["data_simulator"].url == "http://localhost:8080"
        assert settings.messaging["audit.kafka.producer"].audit_channel_name == "audit.audit.events.v1"
        assert settings.data_lake["audit.datalake"].audit_bucket_name == "audit"
        assert settings.data_lake["data-platform.datalake"].checkpoint_path == "s3a://online-shopping/checkpoints/events"


