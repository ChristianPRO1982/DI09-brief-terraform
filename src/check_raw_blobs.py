"""List raw parquet blobs for the selected month range."""

from __future__ import annotations

import logging
from datetime import datetime

from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

from src.azure_blob import AzureBlobClient
from src.config import load_config
from src.logging_utils import configure_logging


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
    load_dotenv()
    configure_logging()
    logger = logging.getLogger("check_raw_blobs")

    cfg = load_config()
    months = iter_months(cfg.start_date, cfg.end_date)

    blob_client = AzureBlobClient(
        connection_string=cfg.azure_storage_connection_string,
        container_name=cfg.azure_container_name,
    )

    all_blobs: list[str] = []
    for month in months:
        prefix = f"yellow_tripdata_{month}"
        names = [b.name for b in blob_client.list_parquet_blobs(prefix=prefix)]
        logger.info("Month=%s prefix=%s found=%d", month, prefix, len(names))
        all_blobs.extend(names)

    logger.info("TOTAL parquet blobs found=%d", len(all_blobs))
    for name in all_blobs[:5]:
        logger.info("Sample blob=%s", name)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
