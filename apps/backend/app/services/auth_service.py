import hmac
from hashlib import sha256

from app.core.config import get_settings
from app.schemas.auth import LoginRequest, LoginResponse
from app.services.customer_service import get_customer_profile


def login(payload: LoginRequest) -> LoginResponse:
    settings = get_settings()
    username_ok = hmac.compare_digest(payload.username, settings.demo_username)
    password_ok = hmac.compare_digest(payload.password, settings.demo_password)
    profile = get_customer_profile()

    if not username_ok or not password_ok:
        return LoginResponse(
            authenticated=False,
            username=payload.username,
            customer_name=profile.customer_name,
            token="",
            reason="kullanici adi veya sifre hatali",
        )

    return LoginResponse(
        authenticated=True,
        username=payload.username,
        customer_name=profile.customer_name,
        token=_token_for(payload.username, settings.demo_password),
    )


def verify_demo_token(token: str) -> bool:
    settings = get_settings()
    expected = _token_for(settings.demo_username, settings.demo_password)
    return bool(token) and hmac.compare_digest(token, expected)


def _token_for(username: str, password: str) -> str:
    settings = get_settings()
    raw = f"{username}:{password}:{settings.app_name}:{settings.app_env}".encode("utf-8")
    return sha256(raw).hexdigest()
