from typing import Protocol

from src.domain.entities.chunk_collection import ChunkCollection
from src.domain.entities.parsed_document import ParsedDocument


class ChunkingEngine(Protocol):
    """Protocol defining text chunking boundary responsibilities."""

    def generate_chunks(self, document: ParsedDocument) -> ChunkCollection:
        """Segments a ParsedDocument into overlapping semantic Chunk entities."""
        ...
