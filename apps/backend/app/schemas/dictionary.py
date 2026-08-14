from pydantic import BaseModel, Field


class DictionaryValidationRequest(BaseModel):
    terms: list[str] = Field(default_factory=list)


class DictionaryValidationItem(BaseModel):
    term: str
    normalized_term: str
    status: str
    sources_checked: list[str] = Field(default_factory=list)
    suggestion: str | None = None


class DictionaryValidationResponse(BaseModel):
    items: list[DictionaryValidationItem] = Field(default_factory=list)
