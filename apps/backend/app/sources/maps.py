from app.schemas.search import SearchRequest
from app.sources.base import LeadSourceAdapter, SourceLead


class MapsLeadAdapter(LeadSourceAdapter):
    source_name = "maps"
    source_type = "maps"

    def collect(self, request: SearchRequest) -> list[SourceLead]:
        if not request.search_maps:
            return []

        keywords = _keywords(request)
        leads: list[SourceLead] = []
        for index, keyword in enumerate(keywords[:3], start=1):
            leads.append(
                SourceLead(
                    company_name=f"{keyword.title()} Maps Company {index}",
                    country=request.target_country,
                    city="Target City",
                    address=f"Industrial Zone {index}, {request.target_country}",
                    website=None,
                    email=None,
                    phone=f"+00 555 010{index}",
                    source=self.source_name,
                    source_type=self.source_type,
                    matched_keyword=keyword,
                    confidence=45 - index,
                    notes="Harita kaynagi icin ornek firma. Gercek API/adaptor baglaninca burada canli veri donecek.",
                )
            )
        return leads


def _keywords(request: SearchRequest) -> list[str]:
    values = [
        request.product_name_en,
        request.product_name_tr,
        *request.related_sectors,
        *request.competitors,
        request.hs_code,
    ]
    return [value for value in values if value]
