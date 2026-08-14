from pydantic import BaseModel, Field


class DemandShareRequest(BaseModel):
    product_name: str
    target_markets: list[str] = Field(default_factory=list)
    message: str
    channels: list[str] = Field(default_factory=list)


class DemandShareJob(BaseModel):
    share_id: str
    product_name: str
    target_markets: list[str] = Field(default_factory=list)
    channels: list[str] = Field(default_factory=list)
    status: str
    queued_at: str
    notes: str
