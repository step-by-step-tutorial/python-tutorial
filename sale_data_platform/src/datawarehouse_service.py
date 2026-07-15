import time

import clickhouse_connect
from clickhouse_connect.driver.exceptions import OperationalError

import config


def create_client():
    retries = 10
    retry_delay_seconds = 3.0

    for attempt in range(1, retries + 1):
        try:
            return clickhouse_connect.get_client(
                host=config.DATAWAREHOUSE_HOST,
                port=config.DATAWAREHOUSE_PORT,
                username=config.DATAWAREHOUSE_USER,
                password=config.DATAWAREHOUSE_PASSWORD
            )
        except OperationalError:
            if attempt == retries:
                raise
            time.sleep(retry_delay_seconds)
    return None
