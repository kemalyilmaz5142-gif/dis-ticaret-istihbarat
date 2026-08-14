from pydantic import BaseModel


class VisitorConsent(BaseModel):
    consent: bool
    country: str | None = None
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    ip_address: str | None = None
    page_url: str | None = None


class VisitorRecord(BaseModel):
    visitor_id: str
    consent: bool
    country: str | None = None
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    ip_address: str | None = None
    company_guess: str | None = None
    isp: str | None = None
    organization: str | None = None
    lookup_confidence: int = 0
    lookup_method: str
    page_url: str | None = None
    notification_title: str = "Yeni web ziyaretçisi"
    notification_message: str | None = None
    created_at: str


class VisitorConsentResponse(BaseModel):
    status: str
    next_step: str
    visitor: VisitorRecord
