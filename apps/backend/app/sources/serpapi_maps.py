import requests

from app.core.config import get_settings
from app.schemas.search import SearchRequest
from app.sources.base import LeadSourceAdapter, SourceLead


class SerpApiMapsAdapter(LeadSourceAdapter):
    source_name = "serpapi-google-maps"
    source_type = "maps"

    def collect(self, request: SearchRequest) -> list[SourceLead]:
        settings = get_settings()
        if not request.search_maps or not settings.serpapi_api_key:
            return []

        keyword = request.product_name_en or request.product_name_tr or request.hs_code
        if not keyword:
            return []

        params = {
            "engine": "google_maps",
            "q": f"{keyword} {request.target_country}",
            "api_key": settings.serpapi_api_key,
            "type": "search",
        }

        try:
            response = requests.get("https://serpapi.com/search.json", params=params, timeout=12)
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError):
            return []

        leads: list[SourceLead] = []
        for item in payload.get("local_results", [])[:10]:
            title = item.get("title")
            if not title:
                continue
            leads.append(
                SourceLead(
                    company_name=title,
                    country=request.target_country,
                    city=None,
                    address=item.get("address"),
                    website=item.get("website"),
                    email=None,
                    phone=item.get("phone"),
                    source=self.source_name,
                    source_type=self.source_type,
                    matched_keyword=keyword,
                    confidence=78,
                    notes="SerpAPI Google Maps sonucu.",
                )
            )

        return leads

