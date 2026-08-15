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


settings = DatabaseSettings(
    host=os.getenv("APP_DATABASE_HOST", "localhost"),
    port=int(os.getenv("APP_DATABASE_PORT", "5432")),
    database_name=os.getenv("APP_DATABASE_NAME", "app_database"),
    user=os.getenv("APP_DATABASE_USER", "admin"),
    password=os.getenv("APP_DATABASE_PASSWORD", "admin"),
    driver=os.getenv("APP_DATABASE_DRIVER", "org.postgresql.Driver"),
    jdbc_url=os.getenv(
        "APP_DATABASE_JDBC_URL",
        "jdbc:postgresql://"
        f"{os.getenv('APP_DATABASE_HOST', 'localhost')}:"
        f"{os.getenv('APP_DATABASE_PORT', '5432')}/"
        f"{os.getenv('APP_DATABASE_NAME', 'app_database')}",
    ),
    sqlalchemy_url=os.getenv(
        "APP_DATABASE_SQLALCHEMY_URL",
        "postgresql+psycopg2://"
        f"{os.getenv('APP_DATABASE_USER', 'admin')}:"
        f"{os.getenv('APP_DATABASE_PASSWORD', 'admin')}@"
        f"{os.getenv('APP_DATABASE_HOST', 'localhost')}:"
        f"{os.getenv('APP_DATABASE_PORT', '5432')}/"
        f"{os.getenv('APP_DATABASE_NAME', 'app_database')}",
    ),
)

