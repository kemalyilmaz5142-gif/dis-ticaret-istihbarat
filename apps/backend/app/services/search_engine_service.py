from app.schemas.search import SearchRequest


SUPPORTED_SEARCH_ENGINES = ["google", "bing", "yandex", "safari"]


def selected_search_engines(request: SearchRequest) -> list[str]:
    engines = [engine.strip().lower() for engine in request.search_engines if engine]
    selected = [engine for engine in engines if engine in SUPPORTED_SEARCH_ENGINES]
    return selected or ["google"]


def engine_label(engine: str) -> str:
    labels = {
        "google": "Google",
        "bing": "Bing",
        "yandex": "Yandex",
        "safari": "Safari/Web",
    }
    return labels.get(engine, engine.title())
