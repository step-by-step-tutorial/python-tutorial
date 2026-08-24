from sqlalchemy import create_engine

from data_platform.config.keys import Key
from data_platform.config.main_settings import settings as main_settings


def create_sale_connection():
    return create_engine(main_settings.database[Key.SALE_DATABASE].sqlalchemy_url)


def create_house_connection():
    return create_engine(main_settings.database[Key.HOUSE_DATABASE].sqlalchemy_url)


def create_online_shopping_connection():
    return create_engine(main_settings.database[Key.ONLINE_SHOPPING_DATABASE].sqlalchemy_url)


def create_audit_connection():
    return create_engine(main_settings.database[Key.AUDIT_DATABASE].sqlalchemy_url)

