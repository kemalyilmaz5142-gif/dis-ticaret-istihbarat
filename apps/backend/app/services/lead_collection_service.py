from app.schemas.search import LeadResult, SearchRequest
from app.sources.base import SourceLead
from app.sources.image_search import ImageSearchAdapter
from app.sources.maps import MapsLeadAdapter
from app.sources.serpapi_maps import SerpApiMapsAdapter
from app.sources.trade_databases import TradeDatabaseAdapter
from app.sources.web_search import WebSearchAdapter


ADAPTERS = (
    ImageSearchAdapter(),
    WebSearchAdapter(),
    SerpApiMapsAdapter(),
    MapsLeadAdapter(),
    TradeDatabaseAdapter(),
)


def collect_leads(request: SearchRequest) -> list[LeadResult]:
    source_leads: list[SourceLead] = []
    for adapter in ADAPTERS:
        source_leads.extend(adapter.collect(request))

    unique_leads = _dedupe(source_leads)
    return [
        LeadResult(
            company_name=lead.company_name,
            country=lead.country,
            city=lead.city,
            address=lead.address,
            website=lead.website,
            email=lead.email,
            phone=lead.phone,
            source=lead.source,
            source_type=lead.source_type,
            matched_keyword=lead.matched_keyword,
            site_category=lead.site_category if lead.site_category != "unknown" else _classify_site_category(lead),
            site_category_reason=lead.site_category_reason or _classify_site_reason(lead),
            score=lead.confidence,
            notes=lead.notes,
        )
        for lead in unique_leads
    ]


def _dedupe(leads: list[SourceLead]) -> list[SourceLead]:
    seen: set[tuple[str, str, str | None]] = set()
    unique: list[SourceLead] = []

    for lead in leads:
        key = (lead.company_name.lower(), lead.country.lower(), lead.website)
        if key in seen:
            continue
        seen.add(key)
        unique.append(lead)

    return sorted(unique, key=lambda item: item.confidence, reverse=True)


def _classify_site_category(lead: SourceLead) -> str:
    text = " ".join(
        item.lower()
        for item in [lead.company_name, lead.website or "", lead.notes or "", lead.matched_keyword]
        if item
    )
    ecommerce_signals = [
        "shop",
        "store",
        "cart",
        "checkout",
        "price",
        "buy",
        "marketplace",
        "amazon",
        "ebay",
        "alibaba",
        "aliexpress",
        "dhgate",
        "indiamart",
        "made-in-china",
        "online",
        "product page",
        "add to cart",
    ]
    company_signals = [
        "manufacturer",
        "factory",
        "producer",
        "supplier",
        "distributor",
        "importer",
        "exporter",
        "company",
        "industrial",
        "about us",
        "corporate",
    ]
    if not lead.website and lead.source_type in {"trade_database", "maps", "image_search"}:
        return "demo_source"
    if lead.source.endswith("search-page") or "arama sayfasi" in text or "arama sayfası" in text:
        return "search_page"
    if any(signal in text for signal in ecommerce_signals):
        return "ecommerce"
    if any(signal in text for signal in company_signals):
        return "company_website"
    if lead.source_type in {"trade_database", "maps", "image_search"}:
        return "demo_source"
    return "company_website" if lead.website else "unknown"


def _classify_site_reason(lead: SourceLead) -> str:
    category = _classify_site_category(lead)
    labels = {
        "ecommerce": "E-ticaret sinyali: shop/store/buy/marketplace gibi kelimeler bulundu.",
        "company_website": "Firma web sitesi sinyali: manufacturer/supplier/importer/distributor gibi kelimeler bulundu.",
        "search_page": "Canli arama motoru veya firma dizini arama sayfasi.",
        "demo_source": "Demo/adaptor kaynak; canli API baglaninca gercek firma verisi gelir.",
        "unknown": "Site tipi kesin belirlenemedi.",
    }
    return labels.get(category, labels["unknown"])
