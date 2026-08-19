from __future__ import annotations

import clickhouse_connect

from config.settings import settings as main_settings


def create_sale_connection():
    return clickhouse_connect.get_client(
        host=main_settings.datawarehouse["sale.datawarehouse"].host,
        port=main_settings.datawarehouse["sale.datawarehouse"].port,
        database=main_settings.datawarehouse["sale.datawarehouse"].database_name,
        username=main_settings.datawarehouse["sale.datawarehouse"].user,
        password=main_settings.datawarehouse["sale.datawarehouse"].password,
    )


def create_house_connection():
    return clickhouse_connect.get_client(
        host=main_settings.datawarehouse["house.datawarehouse"].host,
        port=main_settings.datawarehouse["house.datawarehouse"].port,
        database=main_settings.datawarehouse["house.datawarehouse"].database_name,
        username=main_settings.datawarehouse["house.datawarehouse"].user,
        password=main_settings.datawarehouse["house.datawarehouse"].password,
    )


def create_audit_connection():
    return clickhouse_connect.get_client(
        host=main_settings.datawarehouse["audit.datawarehouse"].host,
        port=main_settings.datawarehouse["audit.datawarehouse"].port,
        database=main_settings.datawarehouse["audit.datawarehouse"].database_name,
        username=main_settings.datawarehouse["audit.datawarehouse"].user,
        password=main_settings.datawarehouse["audit.datawarehouse"].password,
    )
