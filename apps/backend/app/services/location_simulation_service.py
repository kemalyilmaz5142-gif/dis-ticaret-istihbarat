from app.schemas.search import SearchRequest


def location_provider(request: SearchRequest) -> str:
    if not request.simulate_search_location:
        return "none"
    return request.location_provider or "valentin_desktop"


def location_note(request: SearchRequest) -> str:
    if not request.simulate_search_location:
        return "Search runs without location simulation."
    provider = location_provider(request)
    return f"Search should be simulated from {request.target_country} by {provider}."


def location_query_suffix(request: SearchRequest) -> str:
    if not request.simulate_search_location:
        return ""
    return f"near {request.target_country}"
