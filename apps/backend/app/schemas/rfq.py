from pydantic import BaseModel, Field


class RfqScanRequest(BaseModel):
    product_name: str
    target_country: str | None = None
    hs_code: str | None = None
    platforms: list[str] = Field(default_factory=list)


class RfqOpportunity(BaseModel):
    platform: str
    title: str
    buyer_country: str
    quantity_hint: str | None = None
    contact_hint: str | None = None
    score: int
    source_url: str
    notes: str


class RfqScanResponse(BaseModel):
    status: str = "planned"
    opportunities: list[RfqOpportunity] = Field(default_factory=list)
