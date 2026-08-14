from app.automation.query_builder import SearchQuery, build_search_queries
from app.schemas.search import SearchRequest


def plan_search(request: SearchRequest) -> list[SearchQuery]:
    return build_search_queries(request)

