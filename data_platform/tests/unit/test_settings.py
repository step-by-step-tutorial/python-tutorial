from config.settings import settings


class TestMainSettings:

    def test_should_expose_mapped_settings(self) -> None:
        assert settings.app.dataset_name == "Sale"
        assert set(settings.database) == {"data-platform.database", "sale.database", "house.database", "audit.database"}
        assert set(settings.datalake) == {"data-platform.datalake", "sale.datalake", "house.datalake", "audit.datalake"}
        assert set(settings.datawarehouse) == {"data-platform.datawarehouse", "sale.datawarehouse", "house.datawarehouse", "audit.datawarehouse"}
        assert set(settings.messaging) == {
            "sale.kafka.listener",
            "sale.kafka.producer",
            "house.kafka.listener",
            "house.kafka.producer",
            "audit.kafka.producer",
            "audit.kafka.listener",
        }
        assert settings.test_data.download_url == (
            f"http://localhost:8080/datasets/{settings.app.dataset_name.lower()}.json/download?format=json"
        )
        assert settings.messaging["audit.kafka.producer"].audit_channel_name == "sale.audit.event.v1"
        assert settings.datalake["audit.datalake"].audit_bucket_name == "app-datalake-audit"
        assert settings.messaging["sale.kafka.listener"].starting_offsets == "earliest"
        assert settings.datalake["data-platform.datalake"].checkpoint_path == "s3a://app-datalake/checkpoints/sale-events"
