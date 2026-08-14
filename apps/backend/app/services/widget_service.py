import json
from pathlib import Path

from app.schemas.widget import WidgetLeadRecord, WidgetMessageRequest, WidgetMessageResponse


STORAGE_DIR = Path(__file__).resolve().parents[2] / "storage"
WIDGET_LEADS_FILE = STORAGE_DIR / "widget_leads.json"


def answer_widget_message(request: WidgetMessageRequest) -> WidgetMessageResponse:
    lead_captured = bool(request.visitor_email or request.visitor_phone)
    if lead_captured:
        _write_leads([WidgetLeadRecord(**request.model_dump()).model_dump(), *_read_leads()])

    reply = _reply_for(request)
    return WidgetMessageResponse(
        reply=reply,
        next_question="Telefon veya e-posta birakirsaniz ihracat ekibi size donus yapabilir.",
        lead_captured=lead_captured,
    )


def list_widget_leads(limit: int = 50) -> list[WidgetLeadRecord]:
    return [WidgetLeadRecord(**item) for item in _read_leads()[:limit]]


def _reply_for(request: WidgetMessageRequest) -> str:
    if request.language.lower().startswith("en"):
        return "Hello, I can help with product, catalog and export contact requests."
    return "Merhaba, urun, katalog ve ihracat iletisim talepleriniz icin yardimci olabilirim."


def _read_leads() -> list[dict]:
    if not WIDGET_LEADS_FILE.exists():
        return []
    try:
        data = json.loads(WIDGET_LEADS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    return data if isinstance(data, list) else []


def _write_leads(items: list[dict]) -> None:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    WIDGET_LEADS_FILE.write_text(json.dumps(items[:200], indent=2), encoding="utf-8")
