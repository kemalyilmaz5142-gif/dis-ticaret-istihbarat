import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from app.schemas.visitors import VisitorConsent, VisitorRecord
from app.services.ip_lookup_service import lookup_ip


STORAGE_DIR = Path(__file__).resolve().parents[2] / "storage"
VISITORS_FILE = STORAGE_DIR / "visitors.json"


def record_visitor(payload: VisitorConsent, fallback_ip: str | None = None) -> VisitorRecord:
    ip_address = payload.ip_address or fallback_ip
    ip_lookup = lookup_ip(ip_address)
    country = payload.country or ip_lookup.country
    city = payload.city or ip_lookup.city
    lookup_method = "geo_permission" if payload.consent else ip_lookup.lookup_method
    visitor = VisitorRecord(
        visitor_id=str(uuid4()),
        consent=payload.consent,
        country=country,
        city=city,
        latitude=payload.latitude,
        longitude=payload.longitude,
        ip_address=ip_address,
        company_guess=_guess_company(ip_lookup.company_guess, country, payload.consent),
        isp=ip_lookup.isp,
        organization=ip_lookup.organization,
        lookup_confidence=ip_lookup.confidence,
        lookup_method=lookup_method,
        page_url=payload.page_url,
        notification_title="Yeni web ziyaretçisi",
        notification_message=_notification_message(payload.consent, country, city, ip_lookup.company_guess, ip_address),
        created_at=datetime.utcnow().isoformat(),
    )

    rows = _read_rows()
    rows.insert(0, visitor.model_dump())
    _write_rows(rows[:100])
    return visitor


def list_visitors(limit: int = 20) -> list[VisitorRecord]:
    return [VisitorRecord(**row) for row in _read_rows()[:limit]]


def _guess_company(ip_company: str | None, country: str | None, consent: bool) -> str | None:
    if ip_company and ip_company != "Unknown visitor":
        return ip_company
    if consent and country:
        return f"Potential company visitor from {country}"
    return "Unknown visitor"


def _notification_message(consent: bool, country: str | None, city: str | None, company: str | None, ip_address: str | None) -> str:
    location = ", ".join(item for item in [city, country] if item) or "konum bilinmiyor"
    if consent:
        return f"Ziyaretçi konum izni verdi. Tahmini firma: {company or 'henüz bulunamadı'}; konum: {location}."
    return f"Ziyaretçi konum izni vermedi. IP üzerinden takip edilecek: {ip_address or 'IP yok'}; konum: {location}."


def _read_rows() -> list[dict]:
    if not VISITORS_FILE.exists():
        return []
    try:
        data = json.loads(VISITORS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    if not isinstance(data, list):
        return []
    return [row for row in data if isinstance(row, dict)]


def _write_rows(rows: list[dict]) -> None:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    VISITORS_FILE.write_text(json.dumps(rows, ensure_ascii=True, indent=2), encoding="utf-8")
