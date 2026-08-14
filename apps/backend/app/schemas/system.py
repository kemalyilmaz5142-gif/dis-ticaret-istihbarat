from pydantic import BaseModel, Field


class IntegrationStatus(BaseModel):
    code: str
    name: str
    status: str
    detail: str


class SystemStatusResponse(BaseModel):
    app_name: str
    app_env: str
    integrations: list[IntegrationStatus] = Field(default_factory=list)
