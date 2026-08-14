import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import Base, SessionLocal, engine
from app.models.search import LeadResultRecord, SearchRequestRecord
from app.schemas.search import LeadResult, SearchHistoryItem, SearchRequest


STORAGE_DIR = Path(__file__).resolve().parents[2] / "storage"
HISTORY_FILE = STORAGE_DIR / "history.json"


def save_search_history(
    request_id: str,
    status: str,
    request: SearchRequest,
    results: list[LeadResult],
) -> None:
    try:
        Base.metadata.create_all(bind=engine)
        with SessionLocal() as db:
            record = SearchRequestRecord(
                request_id=request_id,
                status=status,
                target_country=request.target_country,
                country_domain=request.country_domain,
                product_name_tr=request.product_name_tr,
                product_name_en=request.product_name_en,
                hs_code=request.hs_code,
                oem_no=request.oem_no,
                competitors=json.dumps(request.competitors, ensure_ascii=True),
                related_sectors=json.dumps(request.related_sectors, ensure_ascii=True),
            )
            record.results = [_to_record(result) for result in results]
            db.add(record)
            db.commit()
    except SQLAlchemyError:
        _save_fallback_history(request_id, status, request, results)


def list_search_history(limit: int = 10) -> list[SearchHistoryItem]:
    try:
        Base.metadata.create_all(bind=engine)
        with SessionLocal() as db:
            records = db.scalars(
                select(SearchRequestRecord).order_by(SearchRequestRecord.created_at.desc()).limit(limit)
            ).all()
            return [
                SearchHistoryItem(
                    request_id=record.request_id,
                    status=record.status,
                    target_country=record.target_country,
                    product_name=record.product_name_en or record.product_name_tr or record.hs_code,
                    result_count=len(record.results),
                    created_at=record.created_at.isoformat(),
                )
                for record in records
            ]
    except SQLAlchemyError:
        return _list_fallback_history(limit)


def _to_record(result: LeadResult) -> LeadResultRecord:
    return LeadResultRecord(
        company_name=result.company_name,
        country=result.country,
        city=result.city,
        address=result.address,
        website=result.website,
        email=result.email,
        phone=result.phone,
        source=result.source,
        source_type=result.source_type,
        matched_keyword=result.matched_keyword,
        score=result.score,
        notes=result.notes,
        ai_fit_reason=result.ai_fit_reason,
        suggested_contact_role=result.suggested_contact_role,
        suggested_contact_emails=json.dumps(result.suggested_contact_emails, ensure_ascii=True),
        suggested_email_subject=result.suggested_email_subject,
        suggested_email_body=result.suggested_email_body,
    )


def _save_fallback_history(
    request_id: str,
    status: str,
    request: SearchRequest,
    results: list[LeadResult],
) -> None:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    current = _read_fallback_rows()
    current.insert(
        0,
        {
            "request_id": request_id,
            "status": status,
            "target_country": request.target_country,
            "product_name": request.product_name_en or request.product_name_tr or request.hs_code,
            "result_count": len(results),
            "created_at": __import__("datetime").datetime.utcnow().isoformat(),
        },
    )
    HISTORY_FILE.write_text(json.dumps(current[:50], ensure_ascii=True, indent=2), encoding="utf-8")


def _list_fallback_history(limit: int) -> list[SearchHistoryItem]:
    return [SearchHistoryItem(**row) for row in _read_fallback_rows()[:limit]]


def _read_fallback_rows() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    if not isinstance(data, list):
        return []
    return [row for row in data if isinstance(row, dict)]
