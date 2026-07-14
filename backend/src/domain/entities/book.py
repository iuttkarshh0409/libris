from datetime import datetime
from typing import ClassVar

from src.domain.value_objects.identifiers import BookId
from src.shared.domain.base import BaseEntity


class Book(BaseEntity):
    """Represents a single textbook uploaded to the platform."""

    VALID_STATUSES: ClassVar[set[str]] = {"queued", "processing", "completed", "failed"}

    def __init__(
        self,
        id: BookId,
        title: str | None,
        author: str | None,
        edition: str | None,
        subject: str | None,
        file_name: str,
        file_path: str,
        upload_timestamp: datetime,
        total_pages: int,
        index_status: str,
    ) -> None:
        super().__init__(id)
        self._title = title
        self._author = author
        self._edition = edition
        self._subject = subject
        self._file_name = file_name
        self._file_path = file_path
        self._upload_timestamp = upload_timestamp
        self._total_pages = total_pages

        if index_status not in self.VALID_STATUSES:
            raise ValueError(
                f"Invalid index status: {index_status}. Must be one of {self.VALID_STATUSES}"
            )
        self._index_status = index_status

    @property
    def id(self) -> BookId:
        assert isinstance(self._id, BookId)
        return self._id

    @property
    def title(self) -> str | None:
        return self._title

    @property
    def author(self) -> str | None:
        return self._author

    @property
    def edition(self) -> str | None:
        return self._edition

    @property
    def subject(self) -> str | None:
        return self._subject

    @property
    def file_name(self) -> str:
        return self._file_name

    @property
    def file_path(self) -> str:
        return self._file_path

    @property
    def upload_timestamp(self) -> datetime:
        return self._upload_timestamp

    @property
    def total_pages(self) -> int:
        return self._total_pages

    @property
    def index_status(self) -> str:
        return self._index_status

    @index_status.setter
    def index_status(self, value: str) -> None:
        if value not in self.VALID_STATUSES:
            raise ValueError(f"Invalid index status: {value}. Must be one of {self.VALID_STATUSES}")
        self._index_status = value
