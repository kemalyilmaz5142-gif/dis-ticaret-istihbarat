from pydantic import BaseModel, Field

from app.schemas.search import LeadResult


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    current_results: list[LeadResult] = Field(default_factory=list)


class ChatSuggestion(BaseModel):
    title: str
    detail: str


class ChatResponse(BaseModel):
    reply: str
    suggestions: list[ChatSuggestion] = Field(default_factory=list)
    status: str = "answered"
