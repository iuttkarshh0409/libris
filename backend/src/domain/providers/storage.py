from typing import Protocol


class StorageProvider(Protocol):
    """Abstraction interface for physical file store persistence operations."""

    def save(self, filename: str, content: bytes) -> str:
        """Saves physical file bytes to the storage location and returns the filepath."""
        ...

    def load(self, file_path: str) -> bytes:
        """Loads physical file bytes from the given filepath location."""
        ...
