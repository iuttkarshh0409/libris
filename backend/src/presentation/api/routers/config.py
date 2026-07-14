from typing import Any

from fastapi import APIRouter
from loguru import logger

from src.infrastructure.configuration import settings
from src.presentation.api.schemas.common import StandardApiResponse, wrap_success
from src.presentation.api.schemas.config import ConfigurationResponse

router = APIRouter(prefix="/config", tags=["configuration"])


@router.get("", response_model=StandardApiResponse[ConfigurationResponse])
async def read_config() -> dict[str, Any]:
    logger.info("Incoming request: GET /config")
    response = ConfigurationResponse(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        similarity_threshold=settings.similarity_threshold,
        retrieval_limit=settings.retrieval_limit,
        embedding_model=settings.embedding_model,
    )
    logger.info("Successful response: GET /config")
    return wrap_success(response)
