from src.domain.providers.storage import StorageProvider


class LocalStorageProvider(StorageProvider):
    """Concrete implementation of local file system storage of original textbooks (placeholder)."""

    def __init__(self, storage_dir: str = "./data/books") -> None:
        self.storage_dir = storage_dir

    def save(self, filename: str, content: bytes) -> str:
        raise NotImplementedError("LocalStorageProvider.save is not implemented.")

    def load(self, file_path: str) -> bytes:
        raise NotImplementedError("LocalStorageProvider.load is not implemented.")
