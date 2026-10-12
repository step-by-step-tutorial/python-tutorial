from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def create_connection(url: str) -> Engine:
    return create_engine(url)
