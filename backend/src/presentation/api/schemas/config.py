from pydantic import BaseModel


class ConfigurationResponse(BaseModel):
    chunk_size: int
    chunk_overlap: int
    similarity_threshold: float
    retrieval_limit: int
    embedding_model: str


class ConfigurationUpdateRequest(BaseModel):
    chunk_size: int | None = None
    chunk_overlap: int | None = None
    similarity_threshold: float | None = None
    retrieval_limit: int | None = None
