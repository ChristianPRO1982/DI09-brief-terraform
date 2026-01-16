"""Debug helper to list raw blobs without assuming naming conventions."""

from __future__ import annotations

import logging

from dotenv import load_dotenv

from src.azure_blob import AzureBlobClient
from src.config import load_config
from src.logging_utils import configure_logging


def main() -> int:
    load_dotenv()
    configure_logging()
    logger = logging.getLogger("debug_list_raw")

    cfg = load_config()
    blob_client = AzureBlobClient(
        connection_string=cfg.azure_storage_connection_string,
        container_name=cfg.azure_container_name,
    )

    count = 0
    for item in blob_client._container.list_blobs():
        logger.info("Blob name=%s size=%s", item.name, getattr(item, "size", None))
        count += 1
        if count >= 50:
            break

    logger.info("Listed blobs=%d (max=50)", count)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
