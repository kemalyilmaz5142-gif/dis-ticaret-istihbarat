from dataclasses import dataclass
from ipaddress import ip_address

import requests

from app.core.config import get_settings


@dataclass(frozen=True)
class IpLookupResult:
    country: str | None = None
    city: str | None = None
    organization: str | None = None
    isp: str | None = None
    company_guess: str | None = None
    lookup_method: str = "ip_lookup"
    confidence: int = 0


def lookup_ip(raw_ip: str | None) -> IpLookupResult:
    settings = get_settings()
    if not raw_ip or not settings.enable_live_ip_lookup or _is_private_ip(raw_ip):
        return IpLookupResult(company_guess="Unknown visitor", lookup_method="local_ip", confidence=10)

    if settings.ipinfo_token:
        result = _lookup_ipinfo(raw_ip, settings.ipinfo_token)
        if result:
            return result

    result = _lookup_ipapi(raw_ip)
    if result:
        return result

    return IpLookupResult(company_guess="Company lookup pending from IP", lookup_method="ip_lookup_failed", confidence=15)


def _lookup_ipinfo(raw_ip: str, token: str) -> IpLookupResult | None:
    try:
        response = requests.get(f"https://ipinfo.io/{raw_ip}/json", params={"token": token}, timeout=8)
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError):
        return None

    org = payload.get("org")
    return IpLookupResult(
        country=payload.get("country"),
        city=payload.get("city"),
        organization=org,
        isp=org,
        company_guess=org or "Company lookup pending from IP",
        lookup_method="ipinfo",
        confidence=65 if org else 45,
    )


def _lookup_ipapi(raw_ip: str) -> IpLookupResult | None:
    try:
        response = requests.get(f"http://ip-api.com/json/{raw_ip}", params={"fields": "status,country,city,isp,org,query"}, timeout=8)
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError):
        return None

    if payload.get("status") != "success":
        return None

    org = payload.get("org") or payload.get("isp")
    return IpLookupResult(
        country=payload.get("country"),
        city=payload.get("city"),
        organization=payload.get("org"),
        isp=payload.get("isp"),
        company_guess=org or "Company lookup pending from IP",
        lookup_method="ip-api",
        confidence=55 if org else 35,
    )


def _is_private_ip(raw_ip: str) -> bool:
    try:
        parsed = ip_address(raw_ip)
    except ValueError:
        return True
    return parsed.is_private or parsed.is_loopback or parsed.is_link_local or parsed.is_reserved
