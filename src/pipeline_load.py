"""Load pipeline: read Parquet from Blob and load into PostgreSQL staging using DuckDB."""

from __future__ import annotations

import logging
import os
import tempfile
import time
from dataclasses import dataclass
from typing import Iterable

import duckdb

from src.azure_blob import AzureBlobClient
from src.postgres import PostgresClient, PostgresDsn


@dataclass(frozen=True)
class LoadMetrics:
    files_processed: int
    rows_loaded: int
    elapsed_seconds: float


class TaxiLoadPipeline:
    def __init__(
        self,
        blob_client: AzureBlobClient,
        pg_client: PostgresClient,
        staging_table: str,
    ) -> None:
        self._blob_client = blob_client
        self._pg_client = pg_client
        self._staging_table = staging_table
        self._logger = logging.getLogger(self.__class__.__name__)

    def run(self, months: Iterable[str], blob_prefix_base: str = "") -> LoadMetrics:
        start_ts = time.time()
        self._pg_client.ensure_staging_table(self._staging_table)

        files_processed = 0
        rows_loaded = 0

        pg_dsn = self._pg_client._dsn.to_dsn_string()

        for month in months:
            prefix = f"{blob_prefix_base}yellow_tripdata_{month}"
            candidates = list(self._blob_client.list_parquet_blobs(prefix=prefix))
            self._logger.info("Month=%s blobs=%d prefix=%s", month, len(candidates), prefix)

            for blob in candidates:
                files_processed += 1
                with tempfile.TemporaryDirectory() as tmpdir:
                    local_path = os.path.join(tmpdir, os.path.basename(blob.name))
                    self._logger.info("Downloading blob=%s size=%s", blob.name, blob.size)
                    self._blob_client.download_to_path(blob.name, local_path)

                    con = duckdb.connect(database=":memory:")
                    con.execute("INSTALL postgres;")
                    con.execute("LOAD postgres;")

                    con.execute(
                        """
                        CREATE TEMP TABLE cleaned AS
                        SELECT
                            row_number() OVER ()::BIGINT AS trip_id,
                            VendorID::INTEGER AS vendor_id,
                            tpep_pickup_datetime::TIMESTAMP AS tpep_pickup_datetime,
                            tpep_dropoff_datetime::TIMESTAMP AS tpep_dropoff_datetime,
                            passenger_count::INTEGER AS passenger_count,
                            trip_distance::DOUBLE AS trip_distance,
                            RatecodeID::INTEGER AS ratecode_id,
                            PULocationID::INTEGER AS pu_location_id,
                            DOLocationID::INTEGER AS do_location_id,
                            payment_type::INTEGER AS payment_type,
                            fare_amount::DOUBLE AS fare_amount,
                            extra::DOUBLE AS extra,
                            mta_tax::DOUBLE AS mta_tax,
                            tip_amount::DOUBLE AS tip_amount,
                            tolls_amount::DOUBLE AS tolls_amount,
                            improvement_surcharge::DOUBLE AS improvement_surcharge,
                            total_amount::DOUBLE AS total_amount,
                            (
                                EXTRACT(EPOCH FROM (tpep_dropoff_datetime::TIMESTAMP - tpep_pickup_datetime::TIMESTAMP))
                                / 60.0
                            )::DOUBLE AS trip_duration_minutes
                        FROM read_parquet(?)
                        WHERE
                            trip_distance IS NOT NULL
                            AND trip_distance > 0
                            AND tpep_pickup_datetime IS NOT NULL
                            AND tpep_dropoff_datetime IS NOT NULL
                            AND tpep_dropoff_datetime >= tpep_pickup_datetime;
                        """,
                        [local_path],
                    )

                    count = con.execute("SELECT COUNT(*) FROM cleaned;").fetchone()[0]
                    self._logger.info("Cleaned rows=%d blob=%s", count, blob.name)

                    con.execute("ATTACH ? AS pg (TYPE postgres);", [pg_dsn])
                    con.execute(f"INSERT INTO pg.public.{self._staging_table} SELECT * FROM cleaned;")
                    rows_loaded += int(count)

                    self._logger.info("Loaded rows=%d into %s", count, self._staging_table)

        elapsed = time.time() - start_ts
        self._logger.info(
            "Load pipeline done files=%d rows=%d elapsed=%.2fs",
            files_processed,
            rows_loaded,
            elapsed,
        )
        return LoadMetrics(files_processed=files_processed, rows_loaded=rows_loaded, elapsed_seconds=elapsed)


def build_pg_client(
    host: str,
    port: int,
    dbname: str,
    user: str,
    password: str,
    sslmode: str,
) -> PostgresClient:
    dsn = PostgresDsn(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
        sslmode=sslmode,
    )
    return PostgresClient(dsn)
