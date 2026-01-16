"""PostgreSQL connection helpers."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote_plus

import psycopg2
from psycopg2.extensions import connection as PgConnection


@dataclass(frozen=True)
class PostgresDsn:
    host: str
    port: int
    dbname: str
    user: str
    password: str
    sslmode: str

    def to_dsn_string(self) -> str:
        return (
            f"host={self.host} port={self.port} dbname={self.dbname} "
            f"user={self.user} password={self.password} sslmode={self.sslmode}"
        )


class PostgresClient:
    def __init__(self, dsn: PostgresDsn) -> None:
        self._dsn = dsn

    def connect(self) -> PgConnection:
        return psycopg2.connect(self._dsn.to_dsn_string())

    def ensure_staging_table(self, table_name: str) -> None:
        create_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            trip_id BIGINT,
            vendor_id INTEGER,
            tpep_pickup_datetime TIMESTAMP,
            tpep_dropoff_datetime TIMESTAMP,
            passenger_count INTEGER,
            trip_distance DOUBLE PRECISION,
            ratecode_id INTEGER,
            pu_location_id INTEGER,
            do_location_id INTEGER,
            payment_type INTEGER,
            fare_amount DOUBLE PRECISION,
            extra DOUBLE PRECISION,
            mta_tax DOUBLE PRECISION,
            tip_amount DOUBLE PRECISION,
            tolls_amount DOUBLE PRECISION,
            improvement_surcharge DOUBLE PRECISION,
            total_amount DOUBLE PRECISION,
            trip_duration_minutes DOUBLE PRECISION
        );
        """
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(create_sql)
            conn.commit()





def build_postgres_uri(
    host: str,
    port: int,
    dbname: str,
    user: str,
    password: str,
    sslmode: str,
) -> str:
    """Build a PostgreSQL URI safe for embedding in DuckDB SQL."""
    user_enc = quote_plus(user)
    pwd_enc = quote_plus(password)
    db_enc = quote_plus(dbname)
    ssl_enc = quote_plus(sslmode)
    return f"postgresql://{user_enc}:{pwd_enc}@{host}:{port}/{db_enc}?sslmode={ssl_enc}"
