"""Load NYC Taxi parquet files from Azure Blob Storage into PostgreSQL staging."""

from __future__ import annotations

import logging
import os
import tempfile
import time

import duckdb
from dotenv import load_dotenv

from src.azure_blob import AzureBlobClient
from src.config import load_config
from src.logging_utils import configure_logging
from src.pipeline_load import build_pg_client


def main() -> int:
    load_dotenv()
    configure_logging()
    logger = logging.getLogger("load_to_postgres")

    cfg = load_config()

    blob_name = f"yellow_tripdata_{cfg.start_date}.parquet"
    logger.info("Loading blob=%s from container=%s", blob_name, cfg.azure_container_name)

    blob_client = AzureBlobClient(
        connection_string=cfg.azure_storage_connection_string,
        container_name=cfg.azure_container_name,
    )

    pg_client = build_pg_client(
        host=cfg.postgres_host,
        port=cfg.postgres_port,
        dbname=cfg.postgres_db,
        user=cfg.postgres_user,
        password=cfg.postgres_password,
        sslmode=cfg.postgres_ssl_mode,
    )

    pg_client.ensure_staging_table(cfg.staging_table)

    start_ts = time.time()
    with tempfile.TemporaryDirectory() as tmpdir:
        local_path = os.path.join(tmpdir, blob_name)
        blob_client.download_to_path(blob_name, local_path)
        logger.info("Downloaded to %s", local_path)

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

        row_count = con.execute("SELECT COUNT(*) FROM cleaned;").fetchone()[0]
        logger.info("Prepared cleaned rows=%d", row_count)

        # pg_dsn = pg_client._dsn.to_dsn_string()
        # con.execute("ATTACH ? AS pg (TYPE postgres);", [pg_dsn])
        from src.postgres import build_postgres_uri

        pg_uri = build_postgres_uri(
            host=cfg.postgres_host,
            port=cfg.postgres_port,
            dbname=cfg.postgres_db,
            user=cfg.postgres_user,
            password=cfg.postgres_password,
            sslmode=cfg.postgres_ssl_mode,
        )

        con.execute(f"ATTACH '{pg_uri}' AS pg (TYPE postgres);")


        con.execute(f"TRUNCATE TABLE pg.public.{cfg.staging_table};")
        con.execute(f"INSERT INTO pg.public.{cfg.staging_table} SELECT * FROM cleaned;")

        logger.info("Loaded rows=%d into %s", row_count, cfg.staging_table)

    elapsed = time.time() - start_ts
    logger.info("Done elapsed=%.2fs", elapsed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
