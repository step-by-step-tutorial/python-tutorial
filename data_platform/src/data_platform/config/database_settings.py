import os
from dataclasses import dataclass
from types import MappingProxyType

from data_platform.config.keys import Key


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


database = MappingProxyType(
    {
        Key.PLATFORM_DATABASE: DatabaseSettings(
            host=os.getenv("PLATFORM_DATABASE_HOST", "localhost"),
            port=int(os.getenv("PLATFORM_DATABASE_PORT", "5432")),
            database_name=os.getenv("PLATFORM_DATABASE_NAME", "app_database"),
            user=os.getenv("PLATFORM_DATABASE_USER", "admin"),
            password=os.getenv("PLATFORM_DATABASE_PASSWORD", "admin"),
            driver=os.getenv("PLATFORM_DATABASE_DRIVER", "org.postgresql.Driver"),
            jdbc_url=os.getenv(
                "PLATFORM_DATABASE_JDBC_URL",
                "jdbc:postgresql://"
                f"{os.getenv('PLATFORM_DATABASE_HOST', 'localhost')}:"
                f"{os.getenv('PLATFORM_DATABASE_PORT', '5432')}/"
                f"{os.getenv('PLATFORM_DATABASE_NAME', 'app_database')}",
            ),
            sqlalchemy_url=os.getenv(
                "PLATFORM_DATABASE_SQLALCHEMY_URL",
                "postgresql+psycopg2://"
                f"{os.getenv('PLATFORM_DATABASE_USER', 'admin')}:"
                f"{os.getenv('PLATFORM_DATABASE_PASSWORD', 'admin')}@"
                f"{os.getenv('PLATFORM_DATABASE_HOST', 'localhost')}:"
                f"{os.getenv('PLATFORM_DATABASE_PORT', '5432')}/"
                f"{os.getenv('PLATFORM_DATABASE_NAME', 'app_database')}",
            ),
        ),
        Key.HOUSE_DATABASE: DatabaseSettings(
            host=os.getenv("DATA_PLATFORM_HOUSE_DATABASE_HOST", "localhost"),
            port=int(os.getenv("DATA_PLATFORM_HOUSE_DATABASE_PORT", "5432")),
            database_name=os.getenv("DATA_PLATFORM_HOUSE_DATABASE_NAME", "app_database"),
            user=os.getenv("DATA_PLATFORM_HOUSE_DATABASE_USER", "admin"),
            password=os.getenv("DATA_PLATFORM_HOUSE_DATABASE_PASSWORD", "admin"),
            driver=os.getenv("DATA_PLATFORM_HOUSE_DATABASE_DRIVER", "org.postgresql.Driver"),
            jdbc_url=os.getenv(
                "DATA_PLATFORM_HOUSE_DATABASE_JDBC_URL",
                "jdbc:postgresql://"
                f"{os.getenv('DATA_PLATFORM_HOUSE_DATABASE_HOST', 'localhost')}:"
                f"{os.getenv('DATA_PLATFORM_HOUSE_DATABASE_PORT', '5432')}/"
                f"{os.getenv('DATA_PLATFORM_HOUSE_DATABASE_NAME', 'app_database')}",
            ),
            sqlalchemy_url=os.getenv(
                "DATA_PLATFORM_HOUSE_DATABASE_SQLALCHEMY_URL",
                "postgresql+psycopg2://"
                f"{os.getenv('DATA_PLATFORM_HOUSE_DATABASE_USER', 'admin')}:"
                f"{os.getenv('DATA_PLATFORM_HOUSE_DATABASE_PASSWORD', 'admin')}@"
                f"{os.getenv('DATA_PLATFORM_HOUSE_DATABASE_HOST', 'localhost')}:"
                f"{os.getenv('DATA_PLATFORM_HOUSE_DATABASE_PORT', '5432')}/"
                f"{os.getenv('DATA_PLATFORM_HOUSE_DATABASE_NAME', 'app_database')}",
            ),
        ),
        Key.ONLINE_SHOPPING_DATABASE: DatabaseSettings(
            host=os.getenv("DATA_PLATFORM_ONLINE_SHOPPING_DATABASE_HOST", "database"),
            port=int(os.getenv("DATA_PLATFORM_ONLINE_SHOPPING_DATABASE_PORT", "5432")),
            database_name=os.getenv("DATA_PLATFORM_ONLINE_SHOPPING_DATABASE_NAME", "app_database"),
            user=os.getenv("DATA_PLATFORM_ONLINE_SHOPPING_DATABASE_USER", "admin"),
            password=os.getenv("DATA_PLATFORM_ONLINE_SHOPPING_DATABASE_PASSWORD", "admin"),
            driver="org.postgresql.Driver",
            jdbc_url=os.getenv("DATA_PLATFORM_ONLINE_SHOPPING_DATABASE_JDBC_URL",
                               "jdbc:postgresql://database:5432/app_database"),
            sqlalchemy_url=os.getenv("DATA_PLATFORM_ONLINE_SHOPPING_DATABASE_SQLALCHEMY_URL",
                                     "postgresql+psycopg2://admin:admin@database:5432/app_database"),
        ),
        Key.AUDIT_DATABASE: DatabaseSettings(
            host=os.getenv("DATA_PLATFORM_AUDIT_DATABASE_HOST", "localhost"),
            port=int(os.getenv("DATA_PLATFORM_AUDIT_DATABASE_PORT", "5432")),
            database_name=os.getenv("DATA_PLATFORM_AUDIT_DATABASE_NAME", "app_database"),
            user=os.getenv("DATA_PLATFORM_AUDIT_DATABASE_USER", "admin"),
            password=os.getenv("DATA_PLATFORM_AUDIT_DATABASE_PASSWORD", "admin"),
            driver=os.getenv("DATA_PLATFORM_AUDIT_DATABASE_DRIVER", "org.postgresql.Driver"),
            jdbc_url=os.getenv(
                "DATA_PLATFORM_AUDIT_DATABASE_JDBC_URL",
                "jdbc:postgresql://"
                f"{os.getenv('DATA_PLATFORM_AUDIT_DATABASE_HOST', 'localhost')}:"
                f"{os.getenv('DATA_PLATFORM_AUDIT_DATABASE_PORT', '5432')}/"
                f"{os.getenv('DATA_PLATFORM_AUDIT_DATABASE_NAME', 'app_database')}",
            ),
            sqlalchemy_url=os.getenv(
                "DATA_PLATFORM_AUDIT_DATABASE_SQLALCHEMY_URL",
                "postgresql+psycopg2://"
                f"{os.getenv('DATA_PLATFORM_AUDIT_DATABASE_USER', 'admin')}:"
                f"{os.getenv('DATA_PLATFORM_AUDIT_DATABASE_PASSWORD', 'admin')}@"
                f"{os.getenv('DATA_PLATFORM_AUDIT_DATABASE_HOST', 'localhost')}:"
                f"{os.getenv('DATA_PLATFORM_AUDIT_DATABASE_PORT', '5432')}/"
                f"{os.getenv('DATA_PLATFORM_AUDIT_DATABASE_NAME', 'app_database')}",
            ),
        ),
    }
)
