from sqlalchemy import create_engine

from app_config import env_config as ec


def create_connection():
    return create_engine(ec.APP_DATABASE_SQLALCHEMY_URL)
