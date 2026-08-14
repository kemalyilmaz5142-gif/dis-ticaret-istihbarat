from app.schemas.dictionary import DictionaryValidationItem, DictionaryValidationRequest, DictionaryValidationResponse
from app.schemas.search import SearchRequest


KNOWN_TERM_HINTS = {
    "automotive spare parts": "automotive spare parts",
    "spare parts": "spare parts",
    "engine": "engine",
    "piston": "piston",
    "hydraulic": "hydraulic",
    "bearing": "bearing",
    "kaynak": "welding",
    "otomotiv": "automotive",
}


def validate_dictionary_terms(payload: DictionaryValidationRequest) -> DictionaryValidationResponse:
    items = [_validate_term(term) for term in payload.terms if term.strip()]
    return DictionaryValidationResponse(items=items)


def terms_from_search_request(request: SearchRequest) -> list[str]:
    terms = [
        request.product_name_tr,
        request.product_name_en,
        request.product_name_es,
        request.product_name_ru,
        request.product_name_ar,
        request.product_name_fr,
        request.product_name_de,
    ]
    return [term for term in terms if term]


def _validate_term(term: str) -> DictionaryValidationItem:
    normalized = " ".join(term.lower().strip().split())
    suggestion = KNOWN_TERM_HINTS.get(normalized)
    status = "matched" if suggestion else "needs_review"
    return DictionaryValidationItem(
        term=term,
        normalized_term=normalized,
        status=status,
        sources_checked=["IATE-ready", "Cambridge-ready", "local-glossary"],
        suggestion=suggestion,
    )
