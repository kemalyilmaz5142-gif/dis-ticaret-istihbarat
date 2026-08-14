from datetime import datetime, timezone
from uuid import uuid4

from app.schemas.fairs import FairListScanRequest, FairParticipantResult, FairScanRequest, FairScanResponse
from app.schemas.modules import AccessCheckRequest
from app.services.module_service import check_access


FAIR_PERSONAS = [
    ("Global Parts Trading", "Hall 4.1 / A22", "import and wholesale"),
    ("Euro Industrial Supply", "Hall 6.0 / C18", "industrial distributor"),
    ("Prime Components GmbH", "Hall 3.1 / B09", "oem and replacement parts"),
    ("Atlas Procurement Group", "Hall 8.0 / D41", "purchasing office"),
    ("Northline Export Buyers", "Hall 5.2 / E14", "cross border sourcing"),
]


def scan_fair_participants(request: FairScanRequest) -> FairScanResponse:
    access = check_access(AccessCheckRequest(module_code="fair_scan"))
    request_id = str(uuid4())
    if not access.allowed:
        return FairScanResponse(
            request_id=request_id,
            status="blocked",
            fair_name=request.fair_name,
            target_country=request.target_country,
            participants=[],
            created_at=_now(),
        )

    participants = [_build_participant(request, index, item) for index, item in enumerate(FAIR_PERSONAS)]
    participants.sort(key=lambda item: item.score, reverse=True)
    return FairScanResponse(
        request_id=request_id,
        status="planned",
        fair_name=request.fair_name,
        target_country=request.target_country,
        participants=participants,
        created_at=_now(),
    )


def scan_fair_list(request: FairListScanRequest) -> FairScanResponse:
    request_id = str(uuid4())
    participants: list[FairParticipantResult] = []
    terms = _matched_terms_from_values(request.product_name, request.sector, request.target_country)

    for index, name in enumerate(request.participant_names[:100], start=1):
        participants.append(
            FairParticipantResult(
                company_name=name,
                country=request.target_country,
                city=_city_hint(request.target_country),
                booth=None,
                website=None,
                email=None,
                matched_terms=terms,
                score=_score_manual_item(name, terms, index),
                source="fair_manual_list",
                notes="Katilimci ismi kullanici listesi uzerinden tarandi.",
            )
        )

    for index, url in enumerate(request.website_urls[:100], start=1):
        participants.append(
            FairParticipantResult(
                company_name=_company_from_url(url),
                country=request.target_country,
                city=_city_hint(request.target_country),
                booth=None,
                website=url,
                email=None,
                matched_terms=terms,
                score=_score_manual_item(url, terms, index),
                source="fair_website_list",
                notes="Web sitesi linki kullanici listesi uzerinden tarandi.",
            )
        )

    participants.sort(key=lambda item: item.score, reverse=True)
    return FairScanResponse(
        request_id=request_id,
        status="planned",
        fair_name=request.fair_name,
        target_country=request.target_country,
        participants=participants[:100],
        created_at=_now(),
    )


def _build_participant(
    request: FairScanRequest,
    index: int,
    persona: tuple[str, str, str],
) -> FairParticipantResult:
    company_base, booth, focus = persona
    terms = _matched_terms(request)
    country_slug = request.target_country.lower().replace(" ", "")
    product_slug = (request.product_name or request.sector or "trade").lower().replace(" ", "-")
    score = min(96, 62 + len(terms) * 8 + (8 if request.fair_website else 0) - index * 3)

    return FairParticipantResult(
        company_name=f"{company_base} {index + 1}",
        country=request.target_country,
        city=_city_hint(request.target_country),
        booth=booth,
        website=f"https://{product_slug}-{country_slug}-{index + 1}.example.com",
        email=f"buyers{index + 1}@{product_slug}-{country_slug}.example.com",
        matched_terms=terms,
        score=score,
        notes=f"{request.fair_name} participant profile matched by {focus}.",
    )


def _matched_terms(request: FairScanRequest) -> list[str]:
    return _matched_terms_from_values(request.product_name, request.sector, request.target_country)


def _matched_terms_from_values(*values: str | None) -> list[str]:
    return [value for value in values if value]


def _score_manual_item(value: str, terms: list[str], index: int) -> int:
    text = value.lower()
    term_hits = sum(1 for term in terms if term.lower() in text)
    return min(96, 58 + term_hits * 14 + max(0, 12 - index))


def _company_from_url(url: str) -> str:
    cleaned = url.replace("https://", "").replace("http://", "").replace("www.", "")
    domain = cleaned.split("/", 1)[0]
    return domain.split(".", 1)[0].replace("-", " ").title() or url


def _city_hint(country: str) -> str | None:
    city_by_country = {
        "germany": "Frankfurt",
        "united kingdom": "London",
        "ingiltere": "London",
        "france": "Paris",
        "italy": "Milan",
        "usa": "Chicago",
        "united states": "Chicago",
    }
    return city_by_country.get(country.strip().lower())


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
