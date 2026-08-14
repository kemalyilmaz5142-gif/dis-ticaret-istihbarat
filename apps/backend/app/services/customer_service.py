import json
from pathlib import Path

from app.schemas.customer import CustomerProfile


STORAGE_DIR = Path(__file__).resolve().parents[2] / "storage"
PROFILE_FILE = STORAGE_DIR / "customer_profile.json"
DEFAULT_PROFILE = CustomerProfile()


def get_customer_profile() -> CustomerProfile:
    if not PROFILE_FILE.exists():
        return DEFAULT_PROFILE
    try:
        return CustomerProfile(**json.loads(PROFILE_FILE.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        return DEFAULT_PROFILE


def save_customer_profile(profile: CustomerProfile) -> CustomerProfile:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    PROFILE_FILE.write_text(json.dumps(profile.model_dump(), indent=2), encoding="utf-8")
    return profile
