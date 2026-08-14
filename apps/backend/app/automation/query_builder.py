from dataclasses import dataclass

from app.schemas.search import SearchRequest
from app.services.country_scope_service import target_countries
from app.services.location_simulation_service import location_query_suffix
from app.services.market_strategy_service import effective_country_domain, market_modifiers, normalize_market_strategy
from app.services.search_engine_service import selected_search_engines


LANGUAGE_FIELDS = {
    "tr": "product_name_tr",
    "en": "product_name_en",
    "es": "product_name_es",
    "ru": "product_name_ru",
    "ar": "product_name_ar",
    "fr": "product_name_fr",
    "de": "product_name_de",
}


@dataclass(frozen=True)
class SearchQuery:
    engine: str
    language: str
    query: str
    target_country: str
    country_domain: str | None
    source_type: str


def build_search_queries(request: SearchRequest) -> list[SearchQuery]:
    queries: list[SearchQuery] = []
    product_names = _product_names_by_language(request)
    modifiers = _intent_modifiers(request)
    strategy = normalize_market_strategy(request.market_strategy)
    engines = selected_search_engines(request)
    countries = target_countries(request)

    if request.search_web:
        for country in countries:
            scoped_request = request.model_copy(update={"target_country": country})
            country_domain = effective_country_domain(scoped_request)
            for engine in engines:
                for language, product_name in product_names.items():
                    for modifier in modifiers:
                        query = _join_terms(product_name, modifier, country_domain, location_query_suffix(scoped_request))
                        queries.append(
                            SearchQuery(
                                engine=f"{engine}-{strategy}",
                                language=language,
                                query=query,
                                target_country=country,
                                country_domain=country_domain,
                                source_type="web",
                            )
                        )

    if request.search_maps:
        for country in countries:
            scoped_request = request.model_copy(update={"target_country": country})
            country_domain = effective_country_domain(scoped_request)
            for language, product_name in product_names.items():
                queries.append(
                    SearchQuery(
                        engine="maps",
                        language=language,
                        query=_join_terms(product_name, "company distributor importer", None, location_query_suffix(scoped_request)),
                        target_country=country,
                        country_domain=country_domain,
                        source_type="maps",
                    )
                )

    return queries[:80]


def _product_names_by_language(request: SearchRequest) -> dict[str, str]:
    values: dict[str, str] = {}
    for language, field_name in LANGUAGE_FIELDS.items():
        value = getattr(request, field_name)
        if value:
            values[language] = value
    for language, value in request.extra_language_terms.items():
        if value:
            values[language] = value

    if not values and request.hs_code:
        values["hs"] = f"HS Code {request.hs_code}"

    if not values and request.oem_no:
        values["oem"] = request.oem_no

    return values


def _intent_modifiers(request: SearchRequest) -> list[str]:
    modifiers = ["importer", "buyer", "distributor", "wholesaler"]

    if request.hs_code:
        modifiers.append(f"HS Code {request.hs_code}")

    if request.oem_no:
        modifiers.append(request.oem_no)

    modifiers.extend(market_modifiers(request))
    modifiers.extend(request.competitors)
    modifiers.extend(request.related_sectors)
    modifiers.extend(request.customer_product_terms)
    modifiers.extend(_site_modifiers(request.potential_customer_websites))
    return list(dict.fromkeys(modifiers))


def _join_terms(product_name: str, modifier: str, country_domain: str | None, location_suffix: str = "") -> str:
    terms = [product_name, modifier]
    if country_domain:
        terms.append(f"site:*{country_domain}")
    if location_suffix:
        terms.append(location_suffix)
    return " ".join(term for term in terms if term).strip()


def _site_modifiers(websites: list[str]) -> list[str]:
    modifiers: list[str] = []
    for website in websites:
        cleaned = website.replace("https://", "").replace("http://", "").strip().strip("/")
        if cleaned:
            modifiers.append(f"similar to {cleaned}")
    return modifiers
