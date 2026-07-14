from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from src.infrastructure.logging import setup_logging
from src.presentation.api import router
from src.presentation.api.schemas.common import wrap_error
from src.shared.exceptions import (
    ConfigurationException,
    DomainException,
    ProviderException,
    RetrievalException,
    ValidationException,
)

# Initialize Logging
setup_logging()

# Initialize FastAPI App
app = FastAPI(
    title="Libris API",
    description="REST API for the Libris Explainable Knowledge Retrieval Platform",
    version="1.0.0",
)

# CORS middleware for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException) -> JSONResponse:
    logger.error(f"Validation failure: {exc}")
    correlation_id = request.headers.get("x-correlation-id") or request.headers.get("x-request-id")
    request_id = request.headers.get("x-request-id")
    error_data = wrap_error(str(exc), request_id=request_id, correlation_id=correlation_id)
    return JSONResponse(status_code=400, content=error_data)


@app.exception_handler(ConfigurationException)
async def configuration_exception_handler(
    request: Request, exc: ConfigurationException
) -> JSONResponse:
    logger.error(f"Configuration failure: {exc}")
    correlation_id = request.headers.get("x-correlation-id") or request.headers.get("x-request-id")
    request_id = request.headers.get("x-request-id")
    error_data = wrap_error(
        "Internal configuration error.", request_id=request_id, correlation_id=correlation_id
    )
    return JSONResponse(status_code=500, content=error_data)


@app.exception_handler(ProviderException)
async def provider_exception_handler(request: Request, exc: ProviderException) -> JSONResponse:
    logger.error(f"Provider failure: {exc}")
    correlation_id = request.headers.get("x-correlation-id") or request.headers.get("x-request-id")
    request_id = request.headers.get("x-request-id")
    error_data = wrap_error(
        "External provider service error.", request_id=request_id, correlation_id=correlation_id
    )
    return JSONResponse(status_code=502, content=error_data)


@app.exception_handler(RetrievalException)
async def retrieval_exception_handler(request: Request, exc: RetrievalException) -> JSONResponse:
    logger.error(f"Retrieval failure: {exc}")
    correlation_id = request.headers.get("x-correlation-id") or request.headers.get("x-request-id")
    request_id = request.headers.get("x-request-id")
    error_data = wrap_error(str(exc), request_id=request_id, correlation_id=correlation_id)
    return JSONResponse(status_code=422, content=error_data)


@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    logger.error(f"Domain failure: {exc}")
    correlation_id = request.headers.get("x-correlation-id") or request.headers.get("x-request-id")
    request_id = request.headers.get("x-request-id")
    error_data = wrap_error(
        "Internal server error occurred.", request_id=request_id, correlation_id=correlation_id
    )
    return JSONResponse(status_code=500, content=error_data)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Unhandled exception: {exc}")
    correlation_id = request.headers.get("x-correlation-id") or request.headers.get("x-request-id")
    request_id = request.headers.get("x-request-id")
    error_data = wrap_error(
        "An unexpected error occurred.", request_id=request_id, correlation_id=correlation_id
    )
    return JSONResponse(status_code=500, content=error_data)


# Include API endpoints
app.include_router(router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Welcome to the Libris API"}
