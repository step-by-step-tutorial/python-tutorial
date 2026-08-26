import logging

from sqlalchemy import create_engine

logger = logging.getLogger(__name__)


def create_connection(url):
    try:
        return create_engine(url)
    except Exception as e:
        logger.error(f"Connecting to database failed due to {e}")
