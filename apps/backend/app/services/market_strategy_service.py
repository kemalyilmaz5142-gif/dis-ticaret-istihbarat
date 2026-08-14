from app.schemas.search import SearchRequest


MARKET_STRATEGIES = {
    "standard": {
        "label": "Standart",
        "modifiers": [],
        "domain": None,
        "notes": "Genel web, harita ve firma veritabani aramasi.",
    },
    "china": {
        "label": "Cin pazari",
        "modifiers": ["importer China", "buyer China", "Alibaba importer", "Made-in-China supplier", "1688 sourcing"],
        "domain": ".cn",
        "notes": "Cin kaynaklari, tedarik platformlari ve ithalatci/satin alma niyetleri oncelenir.",
    },
    "usa": {
        "label": "ABD pazari",
        "modifiers": ["USA importer", "US distributor", "wholesale buyer", "B2B marketplace", "customs broker"],
        "domain": ".com",
        "notes": "ABD distribitorleri, toptancilar, ithalatcilar ve B2B kaynaklari oncelenir.",
    },
}


def normalize_market_strategy(value: str | None) -> str:
    if not value:
        return "standard"
    normalized = value.strip().lower()
    return normalized if normalized in MARKET_STRATEGIES else "standard"


def market_modifiers(request: SearchRequest) -> list[str]:
    strategy = MARKET_STRATEGIES[normalize_market_strategy(request.market_strategy)]
    return list(strategy["modifiers"])


def effective_country_domain(request: SearchRequest) -> str | None:
    if request.country_domain:
        return request.country_domain
    strategy = MARKET_STRATEGIES[normalize_market_strategy(request.market_strategy)]
    domain = strategy["domain"]
    return str(domain) if domain else None


def strategy_notes(request: SearchRequest) -> str:
    strategy = MARKET_STRATEGIES[normalize_market_strategy(request.market_strategy)]
    return str(strategy["notes"])
