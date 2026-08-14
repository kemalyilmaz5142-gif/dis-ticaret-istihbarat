from pydantic import BaseModel, Field


class FairScanRequest(BaseModel):
    fair_name: str = Field(..., examples=["Automechanika Frankfurt"])
    target_country: str = Field(..., examples=["Germany"])
    product_name: str | None = None
    sector: str | None = None
    fair_website: str | None = None


class FairParticipantResult(BaseModel):
    company_name: str
    country: str
    city: str | None = None
    booth: str | None = None
    website: str | None = None
    email: str | None = None
    matched_terms: list[str] = Field(default_factory=list)
    score: int
    source: str = "fair_scan"
    notes: str | None = None


class FairScanResponse(BaseModel):
    request_id: str
    status: str
    fair_name: str
    target_country: str
    participants: list[FairParticipantResult] = Field(default_factory=list)
    created_at: str


class FairListScanRequest(BaseModel):
    fair_name: str = "Manual Fair List"
    target_country: str
    product_name: str | None = None
    sector: str | None = None
    participant_names: list[str] = Field(default_factory=list)
    website_urls: list[str] = Field(default_factory=list)
