from dataclasses import dataclass

from app.schemas.search import SearchRequest


@dataclass(frozen=True)
class SourceLead:
    company_name: str
    country: str
    city: str | None
    address: str | None
    website: str | None
    email: str | None
    phone: str | None
    source: str
    source_type: str
    matched_keyword: str
    confidence: int
    notes: str | None = None
    site_category: str = "unknown"
    site_category_reason: str | None = None


class LeadSourceAdapter:
    source_name = "base"
    source_type = "generic"

    def collect(self, request: SearchRequest) -> list[SourceLead]:
        raise NotImplementedError
