from __future__ import annotations

from sqlalchemy import create_engine

from config.settings import settings as main_settings


def create_sale_connection():
    return create_engine(main_settings.database["sale.database"].sqlalchemy_url)


def create_house_connection():
    return create_engine(main_settings.database["house.database"].sqlalchemy_url)


def create_audit_connection():
    return create_engine(main_settings.database["audit.database"].sqlalchemy_url)
