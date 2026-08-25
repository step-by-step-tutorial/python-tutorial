from data_platform.config.main_settings import settings


class TestMainSettings:

    def test_should_expose_mapped_settings(self) -> None:
        assert settings.app.dataset_name == "Sale"
        assert set(settings.database) == {"data-platform.database", "sale.database", "house.database", "online_shopping.database", "audit.database"}
        assert set(settings.data_lake) == {"data-platform.datalake", "sale.datalake", "house.datalake", "audit.datalake"}
        assert set(settings.warehouse) == {"data-platform.warehouse", "sale.warehouse", "house.warehouse", "online_shopping.warehouse", "audit.warehouse"}
        assert set(settings.messaging) == {
            "sale.kafka.listener",
            "sale.kafka.producer",
            "house.kafka.listener",
            "house.kafka.producer",
            "audit.kafka.producer",
            "audit.kafka.listener",
        }
        assert settings.api["test_data"].url == "http://localhost:8080"
        assert settings.messaging["audit.kafka.producer"].audit_channel_name == "sale.audit.event.v1"
        assert settings.data_lake["audit.datalake"].audit_bucket_name == "app-datalake-audit"
        assert settings.messaging["sale.kafka.listener"].starting_offsets == "earliest"
        assert settings.data_lake["data-platform.datalake"].checkpoint_path == "s3a://app-datalake/checkpoints/sale-events"


