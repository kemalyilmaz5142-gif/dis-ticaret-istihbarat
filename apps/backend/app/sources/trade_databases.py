from app.schemas.search import SearchRequest
from app.services.trade_source_service import selected_trade_sources
from app.sources.base import LeadSourceAdapter, SourceLead


class TradeDatabaseAdapter(LeadSourceAdapter):
    source_name = "trade-databases"
    source_type = "trade_database"

    def collect(self, request: SearchRequest) -> list[SourceLead]:
        keyword = request.hs_code or request.product_name_en or request.product_name_tr or "target product"
        leads: list[SourceLead] = []

        for index, (source_code, database_name) in enumerate(selected_trade_sources(request.trade_database_sources), start=1):
            leads.append(
                SourceLead(
                    company_name=f"{database_name} Matched Importer {index}",
                    country=request.target_country,
                    city=None,
                    address=None,
                    website=None,
                    email=None,
                    phone=None,
                    source=database_name,
                    source_type=self.source_type,
                    matched_keyword=keyword,
                    confidence=54 - index,
                    notes=f"{database_name} kaynak planindan uretildi. API/uyelik bilgisi eklenince canli veri toplanacak.",
                )
            )

        return leads
