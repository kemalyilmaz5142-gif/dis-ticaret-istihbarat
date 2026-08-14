import json
import math
import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from uuid import uuid4

from app.core.config import get_settings
from app.schemas.campaigns import CampaignJob, CampaignPreview, CampaignPreviewRequest, CampaignRecipient


SPAM_WORDS = ["free", "guarantee", "urgent", "limited time", "winner", "click now"]
STORAGE_DIR = Path(__file__).resolve().parents[2] / "storage"
CAMPAIGN_FILE = STORAGE_DIR / "campaigns.json"


def build_campaign_preview(request: CampaignPreviewRequest) -> CampaignPreview:
    recipients = _extract_recipients(request)
    subject = _subject_from_leads(request)
    body = _body_from_leads(request)
    warnings = _spam_warnings(subject, body, recipients)

    return CampaignPreview(
        subject=subject,
        body=body,
        recipients=recipients,
        spam_risk_score=min(100, len(warnings) * 18 + _recipient_risk(recipients)),
        spam_warnings=warnings,
    )


def queue_campaign(preview: CampaignPreview) -> CampaignJob:
    settings = get_settings()
    job = CampaignJob(
        campaign_id=str(uuid4()),
        subject=preview.subject,
        recipient_count=len(preview.recipients),
        spam_risk_score=preview.spam_risk_score,
        status="ready_to_send" if settings.enable_email_sending else "send_disabled",
        send_enabled=settings.enable_email_sending,
        queued_at=datetime.now(timezone.utc).isoformat(),
        batches=max(1, math.ceil(max(1, len(preview.recipients)) / max(1, settings.email_batch_size))),
        warnings=_queue_warnings(preview),
    )
    _write_campaigns([_job_record(job, preview), *_read_campaigns()])
    return job


def list_campaigns(limit: int = 20) -> list[CampaignJob]:
    items = _read_campaigns()[:limit]
    return [CampaignJob(**item["job"]) for item in items if "job" in item]


def send_campaign(campaign_id: str) -> CampaignJob:
    settings = get_settings()
    items = _read_campaigns()
    record = next((item for item in items if item.get("job", {}).get("campaign_id") == campaign_id), None)
    if not record:
        raise ValueError("campaign_not_found")

    job = CampaignJob(**record["job"])
    if not settings.enable_email_sending:
        job.status = "send_disabled"
        record["job"] = job.model_dump()
        _write_campaigns(items)
        return job

    _validate_smtp_settings()
    preview = CampaignPreview(**record["preview"])
    _send_preview_email(preview)
    job.status = "sent"
    record["job"] = job.model_dump()
    _write_campaigns(items)
    return job


def _extract_recipients(request: CampaignPreviewRequest) -> list[CampaignRecipient]:
    recipients: list[CampaignRecipient] = []
    seen: set[str] = set()

    for lead in request.leads:
        emails = lead.suggested_contact_emails or ([lead.email] if lead.email else [])
        for email in emails[:2]:
            normalized = email.lower()
            if normalized in seen:
                continue
            seen.add(normalized)
            recipients.append(
                CampaignRecipient(
                    company_name=lead.company_name,
                    email=normalized,
                    role=lead.suggested_contact_role,
                    source=lead.source,
                )
            )

    return recipients[:50]


def _subject_from_leads(request: CampaignPreviewRequest) -> str:
    for lead in request.leads:
        if lead.suggested_email_subject:
            return lead.suggested_email_subject
    return f"Export cooperation from {request.sender_company}"


def _body_from_leads(request: CampaignPreviewRequest) -> str:
    product_hint = "your product group"
    for lead in request.leads:
        if lead.matched_keyword:
            product_hint = lead.matched_keyword
            break

    catalog_line = f" Catalog: {request.catalog_url}" if request.catalog_url else ""
    return (
        f"Hello,\\n\\n"
        f"We are contacting you from {request.sender_company}. "
        f"We would like to introduce our export capability for {product_hint}. "
        f"If this topic is relevant for your purchasing or import team, we can share technical details, pricing and delivery terms.{catalog_line}\\n\\n"
        f"Best regards"
    )


def _spam_warnings(subject: str, body: str, recipients: list[CampaignRecipient]) -> list[str]:
    text = f"{subject} {body}".lower()
    warnings: list[str] = []

    for word in SPAM_WORDS:
        if word in text:
            warnings.append(f"avoid spam-like word: {word}")

    if len(recipients) > 25:
        warnings.append("send in small batches instead of one large batch")

    if not recipients:
        warnings.append("no verified recipient email candidates")

    if "unsubscribe" not in text:
        warnings.append("add an unsubscribe or opt-out sentence before real sending")

    return warnings


def _recipient_risk(recipients: list[CampaignRecipient]) -> int:
    generic_count = sum(1 for item in recipients if item.email.split("@", 1)[0] in {"info", "contact", "office"})
    return min(35, generic_count * 5)


def _queue_warnings(preview: CampaignPreview) -> list[str]:
    warnings = list(preview.spam_warnings)
    if preview.spam_risk_score >= 70:
        warnings.append("review campaign before enabling SMTP send")
    if len(preview.recipients) == 0:
        warnings.append("campaign has no recipients")
    return warnings


def _job_record(job: CampaignJob, preview: CampaignPreview) -> dict:
    return {"job": job.model_dump(), "preview": preview.model_dump()}


def _read_campaigns() -> list[dict]:
    if not CAMPAIGN_FILE.exists():
        return []
    try:
        return json.loads(CAMPAIGN_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _write_campaigns(items: list[dict]) -> None:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    CAMPAIGN_FILE.write_text(json.dumps(items[:100], indent=2), encoding="utf-8")


def _validate_smtp_settings() -> None:
    settings = get_settings()
    if not settings.smtp_host or not settings.smtp_from_email:
        raise ValueError("smtp_not_configured")


def _send_preview_email(preview: CampaignPreview) -> None:
    settings = get_settings()
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as smtp:
        smtp.starttls()
        if settings.smtp_username:
            smtp.login(settings.smtp_username, settings.smtp_password)
        for recipient in preview.recipients:
            message = EmailMessage()
            message["Subject"] = preview.subject
            message["From"] = settings.smtp_from_email
            message["To"] = recipient.email
            message.set_content(preview.body)
            smtp.send_message(message)
