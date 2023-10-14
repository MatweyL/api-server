import os
from pathlib import Path


def get_project_root():
    return Path(__file__).parent.parent.parent


def get_env_path():
    return os.path.join(get_project_root(), ".env")


def get_db_url(driver: str, host: str, port: int, user: str, password: str, db_name: str):
    return f'{driver}+asyncpg://{user}:{password}@{host}:{port}/{db_name}'
