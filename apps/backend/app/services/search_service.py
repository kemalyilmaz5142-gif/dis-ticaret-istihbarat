from uuid import uuid4
from dataclasses import asdict

from app.schemas.search import SearchRequest, SearchResponse
from app.ai.enrichment import enrich_leads
from app.services.automation_service import plan_search
from app.services.history_service import save_search_history
from app.services.lead_collection_service import collect_leads
from app.services.location_simulation_service import location_note
from app.schemas.modules import AccessCheckRequest
from app.services.module_service import check_access, increment_query_usage
from app.services.market_strategy_service import normalize_market_strategy, strategy_notes


def create_search(request: SearchRequest) -> SearchResponse:
    access = check_access(AccessCheckRequest(module_code="lead_search"))
    if not access.allowed:
        return SearchResponse(
            request_id=str(uuid4()),
            status="blocked",
            query_plan=[],
            results=[],
        )

    market_strategy = normalize_market_strategy(request.market_strategy)
    if market_strategy != "standard":
        strategy_access = check_access(AccessCheckRequest(module_code="market_strategy"))
        if not strategy_access.allowed:
            request.market_strategy = "standard"

    request_id = str(uuid4())
    query_plan = plan_search(request)

    results = enrich_leads(request, collect_leads(request))
    if request.market_strategy != "standard":
        for result in results:
            note = strategy_notes(request)
            result.notes = f"{result.notes or ''} Market strategy: {note}".strip()
    if request.simulate_search_location:
        for result in results:
            result.notes = f"{result.notes or ''} Location simulation: {location_note(request)}".strip()
    save_search_history(
        request_id=request_id,
        status="planned",
        request=request,
        results=results,
    )
    increment_query_usage()

    return SearchResponse(
        request_id=request_id,
        status="planned",
        query_plan=[asdict(query) for query in query_plan],
        results=results,
    )
