from pydantic import BaseModel, Field

from app.schemas.search import LeadResult


class CampaignPreviewRequest(BaseModel):
    leads: list[LeadResult] = Field(default_factory=list)
    sender_company: str = "Demo Export Company"
    catalog_url: str | None = None


class CampaignRecipient(BaseModel):
    company_name: str
    email: str
    role: str | None = None
    source: str


class CampaignPreview(BaseModel):
    subject: str
    body: str
    recipients: list[CampaignRecipient]
    spam_risk_score: int
    spam_warnings: list[str] = Field(default_factory=list)
    status: str = "preview_only"


class CampaignQueueRequest(BaseModel):
    preview: CampaignPreview


class CampaignJob(BaseModel):
    campaign_id: str
    subject: str
    recipient_count: int
    spam_risk_score: int
    status: str
    send_enabled: bool
    queued_at: str
    batches: int
    warnings: list[str] = Field(default_factory=list)
