from config.settings import settings


class TestMainSettings:

    def test_should_expose_mapped_settings(self) -> None:
        assert settings.app.dataset_name == "Sale"
        assert set(settings.database) == {"app.database", "sale.database", "house.database", "audit.database"}
        assert set(settings.datalake) == {"app.datalake", "sale.datalake", "house.datalake", "audit.datalake"}
        assert set(settings.datawarehouse) == {"app.datawarehouse", "sale.datawarehouse", "house.datawarehouse", "audit.datawarehouse"}
        assert set(settings.messaging) == {"sale", "house", "audit"}
        assert set(settings.rest) == {"sale", "house"}
        assert settings.messaging["audit"].audit_channel_name == "sale.audit.event.v1"
        assert settings.datalake["audit.datalake"].audit_bucket_name == "app-datalake-audit"
        assert settings.messaging["sale"].starting_offsets == "earliest"
        assert settings.datalake["app.datalake"].checkpoint_path == "s3a://app-datalake/checkpoints/sale-events"
