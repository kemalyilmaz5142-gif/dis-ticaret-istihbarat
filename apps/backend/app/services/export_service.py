from io import BytesIO

import pandas as pd

from app.schemas.search import LeadResult
from app.schemas.fairs import FairParticipantResult
from app.services.campaign_service import list_campaigns
from app.services.customer_service import get_customer_profile
from app.services.demand_sharing_service import list_demand_shares
from app.services.history_service import list_search_history
from app.services.module_service import get_demo_plan, list_modules
from app.services.system_status_service import get_system_status
from app.services.training_service import list_training_results
from app.services.visitor_service import list_visitors
from app.services.widget_service import list_widget_leads


def build_leads_excel(results: list[LeadResult]) -> BytesIO:
    output = BytesIO()
    columns = [
        "company_name",
        "country",
        "city",
        "address",
        "website",
        "email",
        "phone",
        "source",
        "source_type",
        "matched_keyword",
        "site_category",
        "site_category_reason",
        "score",
        "notes",
        "ai_fit_reason",
        "suggested_contact_role",
        "suggested_contact_emails",
        "suggested_email_subject",
        "suggested_email_body",
    ]
    rows = []
    for result in results:
        row = result.model_dump()
        row["suggested_contact_emails"] = ", ".join(row.get("suggested_contact_emails") or [])
        rows.append(row)
    frame = pd.DataFrame(rows, columns=columns)
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        frame.to_excel(writer, sheet_name="Potansiyel Musteriler", index=False)
    output.seek(0)
    return output


def build_fair_participants_excel(results: list[FairParticipantResult]) -> BytesIO:
    output = BytesIO()
    rows = []
    for result in results:
        row = result.model_dump()
        row["matched_terms"] = ", ".join(row.get("matched_terms") or [])
        rows.append(row)
    frame = pd.DataFrame(
        rows,
        columns=[
            "company_name",
            "country",
            "city",
            "booth",
            "website",
            "email",
            "matched_terms",
            "score",
            "source",
            "notes",
        ],
    )
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        frame.to_excel(writer, sheet_name="Fuar Katilimcilari", index=False)
    output.seek(0)
    return output


def build_operation_report_excel() -> BytesIO:
    output = BytesIO()
    profile = get_customer_profile()
    plan = get_demo_plan()
    system = get_system_status()
    modules = list_modules()
    history = list_search_history(limit=50)
    campaigns = list_campaigns(limit=50)
    visitors = list_visitors(limit=50)
    demand_shares = list_demand_shares(limit=50)
    training_results = list_training_results(limit=50)
    widget_leads = list_widget_leads(limit=50)

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        pd.DataFrame(
            [
                {"metric": "customer_name", "value": plan.customer_name},
                {"metric": "company_name", "value": profile.company_name},
                {"metric": "monthly_query_limit", "value": plan.monthly_query_limit},
                {"metric": "used_queries", "value": plan.used_queries},
                {"metric": "app_name", "value": system.app_name},
                {"metric": "app_env", "value": system.app_env},
            ]
        ).to_excel(writer, sheet_name="Ozet", index=False)

        pd.DataFrame([profile.model_dump()]).to_excel(writer, sheet_name="Musteri Profili", index=False)
        pd.DataFrame([item.model_dump() for item in system.integrations]).to_excel(
            writer,
            sheet_name="Entegrasyonlar",
            index=False,
        )
        pd.DataFrame([item.model_dump() for item in modules]).to_excel(writer, sheet_name="Moduller", index=False)
        pd.DataFrame([item.model_dump() for item in history]).to_excel(writer, sheet_name="Arama Gecmisi", index=False)
        pd.DataFrame([_campaign_row(item) for item in campaigns]).to_excel(writer, sheet_name="Kampanyalar", index=False)
        pd.DataFrame([item.model_dump() for item in visitors]).to_excel(writer, sheet_name="Ziyaretci Bildirimleri", index=False)
        pd.DataFrame([item.model_dump() for item in demand_shares]).to_excel(writer, sheet_name="Talep Paylasimlari", index=False)
        pd.DataFrame([item.model_dump() for item in training_results]).to_excel(writer, sheet_name="Egitim Sonuclari", index=False)
        pd.DataFrame([item.model_dump() for item in widget_leads]).to_excel(writer, sheet_name="Widget Leadleri", index=False)

    output.seek(0)
    return output


def _campaign_row(item) -> dict:
    row = item.model_dump()
    row["warnings"] = ", ".join(row.get("warnings") or [])
    return row
