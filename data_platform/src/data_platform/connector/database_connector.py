from sqlalchemy import Engine, create_engine

from data_platform.model.settings_model import DatabaseSettingsModel


def create_database_engine(settings: DatabaseSettingsModel) -> Engine:
    return create_engine(settings.sqlalchemy_url)
