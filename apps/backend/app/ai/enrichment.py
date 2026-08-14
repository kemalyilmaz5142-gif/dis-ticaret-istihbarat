from dataclasses import dataclass

from app.schemas.search import LeadResult, SearchRequest
from app.services.contact_service import suggest_contact_emails


@dataclass(frozen=True)
class ProductKeywordSet:
    primary_terms: list[str]
    buyer_intents: list[str]
    contact_roles: list[str]


def build_product_keywords(request: SearchRequest) -> ProductKeywordSet:
    primary_terms = [
        value
        for value in [
            request.product_name_en,
            request.product_name_tr,
            request.product_name_de,
            request.product_name_fr,
            request.product_name_es,
            request.product_name_ru,
            request.product_name_ar,
            request.hs_code,
            request.oem_no,
        ]
        if value
    ]
    primary_terms.extend(request.related_sectors)
    primary_terms.extend(request.customer_product_terms)

    buyer_intents = [
        "importer",
        "distributor",
        "wholesaler",
        "purchasing department",
        "procurement manager",
    ]

    contact_roles = [
        "purchasing",
        "procurement",
        "import",
        "sales",
        "general manager",
    ]

    return ProductKeywordSet(
        primary_terms=list(dict.fromkeys(primary_terms)),
        buyer_intents=buyer_intents,
        contact_roles=contact_roles,
    )


def enrich_leads(request: SearchRequest, leads: list[LeadResult]) -> list[LeadResult]:
    keywords = build_product_keywords(request)
    return [_enrich_one(request, lead, keywords) for lead in leads]


def _enrich_one(request: SearchRequest, lead: LeadResult, keywords: ProductKeywordSet) -> LeadResult:
    score = lead.score
    reasons: list[str] = []

    if lead.source_type == "trade_database":
        score += 8
        reasons.append("dis ticaret veritabani eslesmesi")

    if lead.source_type == "maps":
        score += 4
        reasons.append("harita uzerinden fiziksel firma sinyali")

    if lead.email:
        score += 5
        reasons.append("e-posta bilgisi var")

    if lead.website:
        score += 4
        reasons.append("web sitesi var")

    if lead.matched_keyword and lead.matched_keyword in keywords.primary_terms:
        score += 6
        reasons.append("urun veya sektor kelimesi ile eslesti")

    search_text = " ".join(
        item.lower()
        for item in [
            lead.company_name,
            lead.website or "",
            lead.notes or "",
            lead.matched_keyword or "",
        ]
    )
    matched_customer_products = [term for term in request.customer_product_terms if term and term.lower() in search_text]
    excluded_matches = [term for term in request.excluded_product_terms if term and term.lower() in search_text]
    potential_site_matches = [site for site in request.potential_customer_websites if site and site.lower().replace("https://", "").replace("http://", "").strip("/") in search_text]

    if matched_customer_products:
        score += 12
        reasons.append(f"musteri urun kapsami ile uyumlu: {', '.join(matched_customer_products[:2])}")

    if potential_site_matches:
        score += 10
        reasons.append("ornek potansiyel web sitesi profiline benziyor")

    if excluded_matches:
        score -= 18
        reasons.append(f"haric tutulacak urun sinyali var: {', '.join(excluded_matches[:2])}")

    suggested_role = _suggest_contact_role(lead, keywords)
    contact_emails = suggest_contact_emails(lead, suggested_role)
    email_subject = _build_email_subject(request)
    email_body = _build_email_body(request, lead, suggested_role)

    updated = lead.model_copy(
        update={
            "score": min(score, 100),
            "ai_fit_reason": ", ".join(reasons) if reasons else "temel kaynak eslesmesi",
            "suggested_contact_role": suggested_role,
            "suggested_contact_emails": contact_emails,
            "suggested_email_subject": email_subject,
            "suggested_email_body": email_body,
        }
    )
    return updated


def _suggest_contact_role(lead: LeadResult, keywords: ProductKeywordSet) -> str:
    if lead.source_type == "trade_database":
        return "import manager"
    if "distributor" in (lead.matched_keyword or "").lower():
        return "sales or purchasing manager"
    return keywords.contact_roles[0]


def _build_email_subject(request: SearchRequest) -> str:
    product = request.product_name_en or request.product_name_tr or request.hs_code or "product"
    return f"Supply cooperation for {product}"


def _build_email_body(request: SearchRequest, lead: LeadResult, role: str) -> str:
    product = request.product_name_en or request.product_name_tr or "our product group"
    return (
        f"Hello,\\n\\n"
        f"We found {lead.company_name} while researching potential partners in {request.target_country}. "
        f"We would like to contact your {role} about possible cooperation for {product}.\\n\\n"
        f"If relevant, we can share our catalog, technical details and export terms.\\n\\n"
        f"Best regards"
    )
