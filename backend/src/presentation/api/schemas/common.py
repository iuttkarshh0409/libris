import uuid
from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseMetadata(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    api_version: str = "1.0"
    architecture_version: str = "1.0"


class StandardApiResponse(BaseModel, Generic[T]):
    success: bool
    data: T | None = None
    errors: list[str] = Field(default_factory=list)
    metadata: ResponseMetadata = Field(default_factory=ResponseMetadata)


def wrap_success(
    data: Any, request_id: str | None = None, correlation_id: str | None = None
) -> dict[str, Any]:
    req_id = request_id or str(uuid.uuid4())
    corr_id = correlation_id or req_id
    return {
        "success": True,
        "data": data,
        "errors": [],
        "metadata": {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": req_id,
            "correlation_id": corr_id,
            "api_version": "1.0",
            "architecture_version": "1.0",
        },
    }


def wrap_error(
    errors: list[str] | str, request_id: str | None = None, correlation_id: str | None = None
) -> dict[str, Any]:
    err_list = [errors] if isinstance(errors, str) else errors
    req_id = request_id or str(uuid.uuid4())
    corr_id = correlation_id or req_id
    return {
        "success": False,
        "data": None,
        "errors": err_list,
        "metadata": {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": req_id,
            "correlation_id": corr_id,
            "api_version": "1.0",
            "architecture_version": "1.0",
        },
    }
