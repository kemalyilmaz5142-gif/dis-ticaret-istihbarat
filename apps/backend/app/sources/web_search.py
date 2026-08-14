from urllib.parse import parse_qs, quote_plus, unquote, urlparse

import requests
from bs4 import BeautifulSoup

from app.automation.query_builder import build_search_queries
from app.core.config import get_settings
from app.schemas.search import SearchRequest
from app.sources.base import LeadSourceAdapter, SourceLead


class WebSearchAdapter(LeadSourceAdapter):
    source_name = "live-web-search"
    source_type = "web_search"

    def collect(self, request: SearchRequest) -> list[SourceLead]:
        settings = get_settings()
        if not request.search_web or not settings.enable_live_web_search:
            return []

        leads: list[SourceLead] = []
        queries = [query for query in build_search_queries(request) if query.source_type == "web"]

        for query in queries[:8]:
            leads.extend(self._search_duckduckgo(query.engine, query.query, request.target_country, query.query))
            if len(leads) < 4:
                leads.extend(self._search_bing(query.engine, query.query, request.target_country, query.query))
            if len(leads) < 4:
                leads.extend(self._search_duckduckgo_lite(query.engine, query.query, request.target_country, query.query))

        action_links = _public_supplier_and_marketplace_links(request, queries[:4])
        unique_leads = _dedupe_live_results(leads + action_links)
        return unique_leads[:18] if unique_leads else _fallback_public_search_links(request, queries[:4])

    def _search_duckduckgo(self, engine: str, query: str, country: str, matched_keyword: str) -> list[SourceLead]:
        url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
        try:
            response = requests.get(url, headers=_headers(), timeout=8)
            response.raise_for_status()
        except requests.RequestException:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        results: list[SourceLead] = []
        for item in soup.select(".result")[:5]:
            link = item.select_one(".result__a")
            snippet = item.select_one(".result__snippet")
            if not link:
                continue

            title = link.get_text(" ", strip=True)
            href = link.get("href")
            if not title or not href:
                continue

            href = _clean_duckduckgo_url(href)
            if not _is_real_external_url(href):
                continue

            snippet_text = snippet.get_text(" ", strip=True) if snippet else ""
            domain = _domain_from_url(href)
            results.append(
                SourceLead(
                    company_name=_company_name_from_title(title, domain),
                    country=country,
                    city=None,
                    address=None,
                    website=href,
                    email=None,
                    phone=None,
                    source=f"{engine}-duckduckgo-live",
                    source_type=self.source_type,
                    matched_keyword=matched_keyword,
                    confidence=86,
                    notes=snippet_text or f"Canli DuckDuckGo web arama sonucu. Planlanan motor: {engine}.",
                    site_category=_classify_web_result(title, href, snippet_text),
                    site_category_reason="Canli arama sonucunun basligi, linki ve aciklamasina gore siniflandirildi.",
                )
            )
        return results

    def _search_bing(self, engine: str, query: str, country: str, matched_keyword: str) -> list[SourceLead]:
        url = f"https://www.bing.com/search?q={quote_plus(query)}"
        try:
            response = requests.get(url, headers=_headers(), timeout=8)
            response.raise_for_status()
        except requests.RequestException:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        results: list[SourceLead] = []
        for item in soup.select("li.b_algo")[:5]:
            link = item.select_one("h2 a")
            snippet = item.select_one(".b_caption p")
            if not link:
                continue
            title = link.get_text(" ", strip=True)
            href = link.get("href")
            if not title or not href or not _is_real_external_url(href):
                continue
            snippet_text = snippet.get_text(" ", strip=True) if snippet else ""
            domain = _domain_from_url(href)
            results.append(
                SourceLead(
                    company_name=_company_name_from_title(title, domain),
                    country=country,
                    city=None,
                    address=None,
                    website=href,
                    email=None,
                    phone=None,
                    source=f"{engine}-bing-live",
                    source_type=self.source_type,
                    matched_keyword=matched_keyword,
                    confidence=84,
                    notes=snippet_text or f"Canli Bing web arama sonucu. Planlanan motor: {engine}.",
                    site_category=_classify_web_result(title, href, snippet_text),
                    site_category_reason="Canli arama sonucunun basligi, linki ve aciklamasina gore siniflandirildi.",
                )
            )
        return results

    def _search_duckduckgo_lite(self, engine: str, query: str, country: str, matched_keyword: str) -> list[SourceLead]:
        url = f"https://lite.duckduckgo.com/lite/?q={quote_plus(query)}"
        try:
            response = requests.get(url, headers=_headers(), timeout=8)
            response.raise_for_status()
        except requests.RequestException:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        results: list[SourceLead] = []
        for link in soup.select("a.result-link, a[href*='uddg='], a[href^='http']")[:8]:
            title = link.get_text(" ", strip=True)
            href = link.get("href")
            if not title or not href:
                continue
            href = _clean_duckduckgo_url(href)
            if not _is_real_external_url(href):
                continue
            domain = _domain_from_url(href)
            results.append(
                SourceLead(
                    company_name=_company_name_from_title(title, domain),
                    country=country,
                    city=None,
                    address=None,
                    website=href,
                    email=None,
                    phone=None,
                    source=f"{engine}-duckduckgo-lite",
                    source_type=self.source_type,
                    matched_keyword=matched_keyword,
                    confidence=82,
                    notes="Canli DuckDuckGo Lite sonucu. Ucretsiz, API anahtari gerektirmeyen yedek arama yontemi.",
                    site_category=_classify_web_result(title, href, ""),
                    site_category_reason="DuckDuckGo Lite sonucunun basligi ve linkine gore siniflandirildi.",
                )
            )
        return results


def _headers() -> dict[str, str]:
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    }


def _clean_duckduckgo_url(url: str) -> str:
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    if "uddg" in query and query["uddg"]:
        return unquote(query["uddg"][0])
    return url


def _is_real_external_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return False
    domain = parsed.netloc.lower()
    blocked_domains = ("duckduckgo.com", "bing.com", "microsoft.com", "example.com")
    return not any(domain == item or domain.endswith(f".{item}") for item in blocked_domains)


def _dedupe_live_results(leads: list[SourceLead]) -> list[SourceLead]:
    seen: set[str] = set()
    unique: list[SourceLead] = []
    for lead in leads:
        parsed = urlparse(lead.website or "")
        key = f"{parsed.netloc.lower()}{parsed.path.lower()}" if parsed.netloc else lead.company_name.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(lead)
    return unique


def _classify_web_result(title: str, url: str, snippet: str) -> str:
    text = f"{title} {url} {snippet}".lower()
    ecommerce_signals = [
        "shop",
        "store",
        "cart",
        "checkout",
        "buy",
        "price",
        "marketplace",
        "amazon",
        "ebay",
        "alibaba",
        "aliexpress",
        "autodoc",
        "eurocarparts",
        "carparts4less",
        "gsfcarparts",
        "online",
        "basket",
        "product",
        "parts",
        "spares",
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
        "wholesale",
    ]
    if any(signal in text for signal in ecommerce_signals):
        return "ecommerce"
    if any(signal in text for signal in company_signals):
        return "company_website"
    return "company_website"


def _fallback_public_search_links(request: SearchRequest, queries) -> list[SourceLead]:
    return _public_supplier_and_marketplace_links(request, queries)


def _public_supplier_and_marketplace_links(request: SearchRequest, queries) -> list[SourceLead]:
    base_query = (
        " ".join(request.customer_product_terms)
        or request.product_name_en
        or request.product_name_tr
        or request.hs_code
        or "importer distributor"
    )
    country = request.target_country
    query_text = f"{base_query} importer distributor {country}".strip()
    encoded = quote_plus(query_text)
    product_encoded = quote_plus(base_query)
    supplier_encoded = quote_plus(f"{base_query} supplier distributor wholesaler {country}".strip())
    ecommerce_encoded = quote_plus(f"{base_query} buy price online {country}".strip())

    return [
        SourceLead(
            company_name="Euro Car Parts urun aramasi",
            country=country,
            city=None,
            address=None,
            website=f"https://www.eurocarparts.com/search?query={product_encoded}",
            email=None,
            phone=None,
            source="eurocarparts-marketplace-search",
            source_type="web_search",
            matched_keyword=base_query,
            confidence=78,
            notes="Gercek e-ticaret sitesinde urun arama sayfasi. Fiyat ve urun bulunabilirligi kontrol edilir.",
            site_category="ecommerce",
            site_category_reason="E-ticaret arama linki: urun, fiyat ve satin alma sayfasina yonlendirir.",
        ),
        SourceLead(
            company_name="Autodoc urun aramasi",
            country=country,
            city=None,
            address=None,
            website=f"https://www.autodoc.co.uk/spares-search?keyword={product_encoded}",
            email=None,
            phone=None,
            source="autodoc-marketplace-search",
            source_type="web_search",
            matched_keyword=base_query,
            confidence=77,
            notes="Gercek e-ticaret yedek parca arama sayfasi.",
            site_category="ecommerce",
            site_category_reason="E-ticaret arama linki: urun, fiyat ve satin alma sayfasina yonlendirir.",
        ),
        SourceLead(
            company_name="eBay UK urun aramasi",
            country=country,
            city=None,
            address=None,
            website=f"https://www.ebay.co.uk/sch/i.html?_nkw={product_encoded}",
            email=None,
            phone=None,
            source="ebay-marketplace-search",
            source_type="web_search",
            matched_keyword=base_query,
            confidence=76,
            notes="Gercek pazar yeri aramasi. Satici ve urun fiyatlarini gormek icin kullanilir.",
            site_category="ecommerce",
            site_category_reason="E-ticaret/pazar yeri arama linki.",
        ),
        SourceLead(
            company_name="Google Shopping urun aramasi",
            country=country,
            city=None,
            address=None,
            website=f"https://www.google.com/search?tbm=shop&q={ecommerce_encoded}",
            email=None,
            phone=None,
            source="google-shopping-search",
            source_type="web_search",
            matched_keyword=f"{base_query} buy price online",
            confidence=75,
            notes="Google Shopping uzerinden gercek e-ticaret sonuclari acilir.",
            site_category="ecommerce",
            site_category_reason="Alisveris sonuclari arama linki.",
        ),
        SourceLead(
            company_name="Bing tedarikci arama sayfasi",
            country=country,
            city=None,
            address=None,
            website=f"https://www.bing.com/search?q={supplier_encoded}",
            email=None,
            phone=None,
            source="bing-supplier-search-page",
            source_type="web_search",
            matched_keyword=f"{base_query} supplier distributor wholesaler",
            confidence=76,
            notes="Bing uzerinden tedarikci, distributor ve toptanci aramasi acilir.",
            site_category="search_page",
            site_category_reason="Tedarikci bulmak icin acilan gercek arama motoru sayfasi.",
        ),
        SourceLead(
            company_name="DuckDuckGo tedarikci arama sayfasi",
            country=country,
            city=None,
            address=None,
            website=f"https://duckduckgo.com/html/?q={supplier_encoded}",
            email=None,
            phone=None,
            source="duckduckgo-supplier-search-page",
            source_type="web_search",
            matched_keyword=f"{base_query} supplier distributor wholesaler",
            confidence=75,
            notes="DuckDuckGo uzerinden ucretsiz tedarikci aramasi.",
            site_category="search_page",
            site_category_reason="Tedarikci bulmak icin acilan gercek arama motoru sayfasi.",
        ),
        SourceLead(
            company_name="Europages tedarikci arama sayfasi",
            country=country,
            city=None,
            address=None,
            website=f"https://www.europages.co.uk/companies/{encoded}.html",
            email=None,
            phone=None,
            source="europages-public-search",
            source_type="web_search",
            matched_keyword=query_text,
            confidence=74,
            notes="Europages tedarikci rehberinde gercek firma aramasi acilir.",
            site_category="company_website",
            site_category_reason="Firma rehberi/toptanci arama linki; tedarikci bulma amacli.",
        ),
        SourceLead(
            company_name="Kompass tedarikci arama sayfasi",
            country=country,
            city=None,
            address=None,
            website=f"https://tr.kompass.com/searchCompanies?text={encoded}",
            email=None,
            phone=None,
            source="kompass-public-search",
            source_type="web_search",
            matched_keyword=query_text,
            confidence=73,
            notes="Kompass firma rehberinde gercek tedarikci aramasi acilir.",
            site_category="company_website",
            site_category_reason="Firma rehberi/toptanci arama linki; tedarikci bulma amacli.",
        ),
        SourceLead(
            company_name="Google firma iletisim aramasi",
            country=country,
            city=None,
            address=None,
            website=f"https://www.google.com/search?q={quote_plus(f'{base_query} supplier distributor contact email {country}'.strip())}",
            email=None,
            phone=None,
            source="google-contact-search-page",
            source_type="web_search",
            matched_keyword=f"{base_query} supplier distributor contact email",
            confidence=72,
            notes="Tedarikci web sitesi, iletisim sayfasi, e-posta ve telefon bulmak icin gercek Google aramasi.",
            site_category="search_page",
            site_category_reason="Tedarikci iletisim bilgisi bulmak icin acilan gercek arama sayfasi.",
        ),
    ]


def _domain_from_url(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.netloc:
        return parsed.netloc.removeprefix("www.")
    return None


def _company_name_from_title(title: str, domain: str | None) -> str:
    if " - " in title:
        return title.split(" - ", 1)[0][:120]
    if " | " in title:
        return title.split(" | ", 1)[0][:120]
    if domain:
        return domain.split(".", 1)[0].replace("-", " ").title()
    return title[:120]
