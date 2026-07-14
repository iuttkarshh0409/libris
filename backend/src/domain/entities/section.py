from src.domain.value_objects.identifiers import ChapterId, SectionId
from src.shared.domain.base import BaseEntity


class Section(BaseEntity):
    """Represents a logical section within a Chapter."""

    def __init__(
        self,
        id: SectionId,
        chapter_id: ChapterId,
        title: str,
        start_page: int,
        end_page: int,
    ) -> None:
        super().__init__(id)
        self._chapter_id = chapter_id
        self._title = title
        self._start_page = start_page
        self._end_page = end_page

    @property
    def id(self) -> SectionId:
        assert isinstance(self._id, SectionId)
        return self._id

    @property
    def chapter_id(self) -> ChapterId:
        return self._chapter_id

    @property
    def title(self) -> str:
        return self._title

    @property
    def start_page(self) -> int:
        return self._start_page

    @property
    def end_page(self) -> int:
        return self._end_page
