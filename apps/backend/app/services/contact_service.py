from urllib.parse import urlparse

from app.schemas.search import LeadResult


ROLE_PREFIXES = [
    "purchasing",
    "procurement",
    "import",
    "buyer",
    "sales",
    "manager",
]


def suggest_contact_emails(lead: LeadResult, role: str | None = None) -> list[str]:
    domain = _domain_from_lead(lead)
    if not domain:
        return []

    candidates: list[str] = []
    role_prefix = _prefix_from_role(role)
    if role_prefix:
        candidates.append(f"{role_prefix}@{domain}")

    for prefix in ROLE_PREFIXES:
        candidates.append(f"{prefix}@{domain}")

    if lead.email and not _is_generic_email(lead.email):
        candidates.insert(0, lead.email)

    return list(dict.fromkeys(candidates))[:6]


def _domain_from_lead(lead: LeadResult) -> str | None:
    if lead.website:
        parsed = urlparse(lead.website)
        domain = parsed.netloc or parsed.path
        domain = domain.removeprefix("www.").split("/")[0]
        if "." in domain:
            return domain.lower()

    if lead.email and "@" in lead.email:
        return lead.email.split("@", 1)[1].lower()

    return None


def _prefix_from_role(role: str | None) -> str | None:
    if not role:
        return None
    normalized = role.lower()
    if "purchase" in normalized:
        return "purchasing"
    if "procurement" in normalized:
        return "procurement"
    if "import" in normalized:
        return "import"
    if "sales" in normalized:
        return "sales"
    if "manager" in normalized:
        return "manager"
    return None


def _is_generic_email(email: str) -> bool:
    prefix = email.split("@", 1)[0].lower()
    return prefix in {"info", "contact", "hello", "office", "admin"}
