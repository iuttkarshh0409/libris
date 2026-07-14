from src.domain.entities.chunk_collection import ChunkCollection
from src.domain.entities.parsed_document import ParsedDocument


class DefaultChunkingEngine:
    """Default implementation of ChunkingEngine that raises NotImplementedError."""

    def generate_chunks(self, document: ParsedDocument) -> ChunkCollection:
        raise NotImplementedError("DefaultChunkingEngine.generate_chunks is not implemented.")
