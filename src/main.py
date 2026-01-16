"""CLI entrypoint for pipelines."""

from __future__ import annotations

from dotenv import load_dotenv

import logging
import sys
from datetime import datetime

from dateutil.relativedelta import relativedelta

from src.azure_blob import AzureBlobClient
from src.config import load_config
from src.logging_utils import configure_logging
from src.pipeline_load import TaxiLoadPipeline, build_pg_client


load_dotenv()


def iter_months(start_yyyy_mm: str, end_yyyy_mm: str) -> list[str]:
    start = datetime.strptime(start_yyyy_mm, "%Y-%m")
    end = datetime.strptime(end_yyyy_mm, "%Y-%m")

    months: list[str] = []
    cur = start
    while cur <= end:
        months.append(cur.strftime("%Y-%m"))
        cur = cur + relativedelta(months=1)
    return months


def main() -> int:
    configure_logging()
    logger = logging.getLogger("main")

    cfg = load_config()
    command = sys.argv[1] if len(sys.argv) > 1 else "load"

    if command != "load":
        logger.error("Unknown command=%s (supported: load)", command)
        return 2

    months = iter_months(cfg.start_date, cfg.end_date)
    logger.info("Running load months=%s", ",".join(months))

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

    pipeline = TaxiLoadPipeline(
        blob_client=blob_client,
        pg_client=pg_client,
        staging_table=cfg.staging_table,
    )
    pipeline.run(months=months)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
