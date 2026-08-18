from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class DatabaseSettings:
    host: str
    port: int
    database_name: str
    user: str
    password: str
    driver: str
    jdbc_url: str
    sqlalchemy_url: str


sale_settings = DatabaseSettings(
    host=os.getenv("APP_SALE_DATABASE_HOST", "localhost"),
    port=int(os.getenv("APP_SALE_DATABASE_PORT", "5432")),
    database_name=os.getenv("APP_SALE_DATABASE_NAME", "app_database"),
    user=os.getenv("APP_SALE_DATABASE_USER", "admin"),
    password=os.getenv("APP_SALE_DATABASE_PASSWORD", "admin"),
    driver=os.getenv("APP_SALE_DATABASE_DRIVER", "org.postgresql.Driver"),
    jdbc_url=os.getenv(
        "APP_SALE_DATABASE_JDBC_URL",
        "jdbc:postgresql://"
        f"{os.getenv('APP_SALE_DATABASE_HOST', 'localhost')}:"
        f"{os.getenv('APP_SALE_DATABASE_PORT', '5432')}/"
        f"{os.getenv('APP_SALE_DATABASE_NAME', 'app_database')}",
    ),
    sqlalchemy_url=os.getenv(
        "APP_SALE_DATABASE_SQLALCHEMY_URL",
        "postgresql+psycopg2://"
        f"{os.getenv('APP_SALE_DATABASE_USER', 'admin')}:"
        f"{os.getenv('APP_SALE_DATABASE_PASSWORD', 'admin')}@"
        f"{os.getenv('APP_SALE_DATABASE_HOST', 'localhost')}:"
        f"{os.getenv('APP_SALE_DATABASE_PORT', '5432')}/"
        f"{os.getenv('APP_SALE_DATABASE_NAME', 'app_database')}",
    ),
)
house_settings = DatabaseSettings(
    host=os.getenv("APP_HOUSE_DATABASE_HOST", "localhost"),
    port=int(os.getenv("APP_HOUSE_DATABASE_PORT", "5432")),
    database_name=os.getenv("APP_HOUSE_DATABASE_NAME", "app_database"),
    user=os.getenv("APP_HOUSE_DATABASE_USER", "admin"),
    password=os.getenv("APP_HOUSE_DATABASE_PASSWORD", "admin"),
    driver=os.getenv("APP_HOUSE_DATABASE_DRIVER", "org.postgresql.Driver"),
    jdbc_url=os.getenv(
        "APP_HOUSE_DATABASE_JDBC_URL",
        "jdbc:postgresql://"
        f"{os.getenv('APP_HOUSE_DATABASE_HOST', 'localhost')}:"
        f"{os.getenv('APP_HOUSE_DATABASE_PORT', '5432')}/"
        f"{os.getenv('APP_HOUSE_DATABASE_NAME', 'app_database')}",
    ),
    sqlalchemy_url=os.getenv(
        "APP_HOUSE_DATABASE_SQLALCHEMY_URL",
        "postgresql+psycopg2://"
        f"{os.getenv('APP_HOUSE_DATABASE_USER', 'admin')}:"
        f"{os.getenv('APP_HOUSE_DATABASE_PASSWORD', 'admin')}@"
        f"{os.getenv('APP_HOUSE_DATABASE_HOST', 'localhost')}:"
        f"{os.getenv('APP_HOUSE_DATABASE_PORT', '5432')}/"
        f"{os.getenv('APP_HOUSE_DATABASE_NAME', 'app_database')}",
    ),
)
audit_settings = DatabaseSettings(
    host=os.getenv("APP_AUDIT_DATABASE_HOST", "localhost"),
    port=int(os.getenv("APP_AUDIT_DATABASE_PORT", "5432")),
    database_name=os.getenv("APP_AUDIT_DATABASE_NAME", "app_database"),
    user=os.getenv("APP_AUDIT_DATABASE_USER", "admin"),
    password=os.getenv("APP_AUDIT_DATABASE_PASSWORD", "admin"),
    driver=os.getenv("APP_AUDIT_DATABASE_DRIVER", "org.postgresql.Driver"),
    jdbc_url=os.getenv(
        "APP_AUDIT_DATABASE_JDBC_URL",
        "jdbc:postgresql://"
        f"{os.getenv('APP_AUDIT_DATABASE_HOST', 'localhost')}:"
        f"{os.getenv('APP_AUDIT_DATABASE_PORT', '5432')}/"
        f"{os.getenv('APP_AUDIT_DATABASE_NAME', 'app_database')}",
    ),
    sqlalchemy_url=os.getenv(
        "APP_AUDIT_DATABASE_SQLALCHEMY_URL",
        "postgresql+psycopg2://"
        f"{os.getenv('APP_AUDIT_DATABASE_USER', 'admin')}:"
        f"{os.getenv('APP_AUDIT_DATABASE_PASSWORD', 'admin')}@"
        f"{os.getenv('APP_AUDIT_DATABASE_HOST', 'localhost')}:"
        f"{os.getenv('APP_AUDIT_DATABASE_PORT', '5432')}/"
        f"{os.getenv('APP_AUDIT_DATABASE_NAME', 'app_database')}",
    ),
)

# Backward-compatible default alias.
settings = sale_settings
