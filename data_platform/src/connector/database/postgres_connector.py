from sqlalchemy import create_engine

from config.database import settings as database_settings


def create_connection():
    return create_engine(database_settings.sqlalchemy_url)
