"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    azure_storage_connection_string: str
    azure_container_name: str

    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_ssl_mode: str

    start_date: str
    end_date: str
    staging_table: str


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def load_config() -> AppConfig:
    return AppConfig(
        azure_storage_connection_string=_require_env("AZURE_STORAGE_CONNECTION_STRING"),
        azure_container_name=os.getenv("AZURE_CONTAINER_NAME", "raw"),
        postgres_host=_require_env("POSTGRES_HOST"),
        postgres_port=int(os.getenv("POSTGRES_PORT", "5432")),
        postgres_db=os.getenv("POSTGRES_DB", "citus"),
        postgres_user=_require_env("POSTGRES_USER"),
        postgres_password=_require_env("POSTGRES_PASSWORD"),
        postgres_ssl_mode=os.getenv("POSTGRES_SSL_MODE", "require"),
        start_date=_require_env("START_DATE"),
        end_date=_require_env("END_DATE"),
        staging_table=os.getenv("STAGING_TABLE", "staging_taxi_trips"),
    )
