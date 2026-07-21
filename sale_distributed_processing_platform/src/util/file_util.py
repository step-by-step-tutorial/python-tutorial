from app_config import env_config as ec


def load_sql_query(file_name: str) -> str:
    return (ec.SQL_DIR / file_name).read_text(encoding="utf-8").strip()
