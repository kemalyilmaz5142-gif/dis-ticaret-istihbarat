from pydantic import BaseModel


class WidgetMessageRequest(BaseModel):
    message: str
    page_url: str | None = None
    visitor_email: str | None = None
    visitor_phone: str | None = None
    language: str = "tr"


class WidgetMessageResponse(BaseModel):
    reply: str
    next_question: str
    lead_captured: bool = False


class WidgetLeadRecord(BaseModel):
    visitor_email: str | None = None
    visitor_phone: str | None = None
    message: str
    page_url: str | None = None
    language: str
