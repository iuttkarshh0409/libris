from typing import Any

from fastapi import APIRouter
from loguru import logger

from src.application.container import container
from src.infrastructure.configuration import settings
from src.presentation.api.schemas.common import StandardApiResponse, wrap_success
from src.presentation.api.schemas.status import StatusResponse

router = APIRouter(prefix="/status", tags=["status"])


@router.get("", response_model=StandardApiResponse[StatusResponse])
async def system_status() -> dict[str, Any]:
    logger.info("Incoming request: GET /status")

    try:
        index_version = container.index_provider.provider_version
        index_status = f"healthy (version: {index_version})"
    except Exception as e:
        index_status = f"unhealthy: {e}"

    try:
        emb_version = container.embedding_provider.provider_version
        emb_status = f"healthy (version: {emb_version})"
    except Exception as e:
        emb_status = f"unhealthy: {e}"

    try:
        llm_status = "healthy"
    except Exception as e:
        llm_status = f"unhealthy: {e}"

    provider_status = {
        "index_provider": index_status,
        "embedding_provider": emb_status,
        "llm_provider": llm_status,
    }

    configured_models = {
        "embedding_model": settings.embedding_model,
        "llm_model": "gemini-1.5-pro",
    }

    all_healthy = all("healthy" in status for status in provider_status.values())
    health_state = "healthy" if all_healthy else "unhealthy"

    response = StatusResponse(
        application_version="1.0.0",
        architecture_version="1.0.0",
        provider_status=provider_status,
        configured_models=configured_models,
        health_state=health_state,
    )
    logger.info("Successful response: GET /status")
    return wrap_success(response)
