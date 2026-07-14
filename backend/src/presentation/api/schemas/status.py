from pydantic import BaseModel


class SystemStatusResponse(BaseModel):
    status: str
    components: dict[str, str]


class StatusResponse(BaseModel):
    application_version: str
    architecture_version: str
    provider_status: dict[str, str]
    configured_models: dict[str, str]
    health_state: str
