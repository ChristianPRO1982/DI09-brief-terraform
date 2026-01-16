"""Azure Blob Storage helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from azure.storage.blob import BlobServiceClient


@dataclass(frozen=True)
class BlobObject:
    name: str
    size: Optional[int]


class AzureBlobClient:
    def __init__(self, connection_string: str, container_name: str) -> None:
        self._service = BlobServiceClient.from_connection_string(connection_string)
        self._container = self._service.get_container_client(container_name)

    def list_parquet_blobs(self, prefix: str) -> Iterable[BlobObject]:
        for item in self._container.list_blobs(name_starts_with=prefix):
            if item.name.endswith(".parquet"):
                yield BlobObject(name=item.name, size=getattr(item, "size", None))

    def download_to_path(self, blob_name: str, local_path: str) -> None:
        blob = self._container.get_blob_client(blob_name)
        with open(local_path, "wb") as f:
            stream = blob.download_blob()
            stream.readinto(f)
