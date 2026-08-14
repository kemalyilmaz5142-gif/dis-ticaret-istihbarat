import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.schemas.demand_sharing import DemandShareJob, DemandShareRequest


STORAGE_DIR = Path(__file__).resolve().parents[2] / "storage"
DEMAND_SHARE_FILE = STORAGE_DIR / "demand_shares.json"


def queue_demand_share(request: DemandShareRequest) -> DemandShareJob:
    job = DemandShareJob(
        share_id=str(uuid4()),
        product_name=request.product_name,
        target_markets=request.target_markets,
        channels=request.channels or ["manual_review"],
        status="queued_for_review",
        queued_at=datetime.now(timezone.utc).isoformat(),
        notes="Guvenli demo modu: talep paylasimi dis platformlara otomatik yayinlanmaz; once manuel onay gerekir.",
    )
    _write_jobs([job.model_dump(), *_read_jobs()])
    return job


def list_demand_shares(limit: int = 20) -> list[DemandShareJob]:
    return [DemandShareJob(**item) for item in _read_jobs()[:limit]]


def _read_jobs() -> list[dict]:
    if not DEMAND_SHARE_FILE.exists():
        return []
    try:
        data = json.loads(DEMAND_SHARE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    return data if isinstance(data, list) else []


def _write_jobs(items: list[dict]) -> None:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    DEMAND_SHARE_FILE.write_text(json.dumps(items[:100], indent=2), encoding="utf-8")
