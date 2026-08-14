from fastapi import APIRouter, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse

from app.ai.enrichment import build_product_keywords

from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.campaigns import CampaignJob, CampaignPreview, CampaignPreviewRequest, CampaignQueueRequest
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.customer import CustomerProfile
from app.schemas.demand_sharing import DemandShareJob, DemandShareRequest
from app.schemas.dictionary import DictionaryValidationRequest, DictionaryValidationResponse
from app.schemas.fairs import FairListScanRequest, FairScanRequest, FairScanResponse
from app.schemas.modules import AccessCheckRequest, AccessCheckResponse, ModuleInfo, SubscriptionPlan
from app.schemas.rfq import RfqScanRequest, RfqScanResponse
from app.schemas.search import ImageUploadResponse, KeywordPreview, SearchHistoryItem, SearchRequest, SearchResponse
from app.schemas.system import SystemStatusResponse
from app.schemas.trade_sources import TradeSourceStatusResponse
from app.schemas.training import TrainingLesson, TrainingQuizResult, TrainingQuizSubmission
from app.schemas.widget import WidgetLeadRecord, WidgetMessageRequest, WidgetMessageResponse
from app.schemas.visitors import VisitorConsent, VisitorConsentResponse, VisitorRecord
from app.services.auth_service import login
from app.services.campaign_service import build_campaign_preview, list_campaigns, queue_campaign, send_campaign
from app.services.chat_service import answer_chat
from app.services.customer_service import get_customer_profile, save_customer_profile
from app.services.demand_sharing_service import list_demand_shares, queue_demand_share
from app.services.dictionary_service import terms_from_search_request, validate_dictionary_terms
from app.services.export_service import build_fair_participants_excel, build_leads_excel, build_operation_report_excel
from app.services.fair_service import scan_fair_list, scan_fair_participants
from app.services.history_service import list_search_history
from app.services.image_service import save_product_image
from app.services.module_service import check_access, get_demo_plan, list_modules, reset_query_usage
from app.services.rfq_service import scan_rfq_opportunities
from app.services.search_service import create_search
from app.services.system_status_service import get_system_status
from app.services.trade_source_service import list_trade_sources
from app.services.training_service import list_training_lessons, list_training_results, submit_training_quiz
from app.services.visitor_service import list_visitors, record_visitor
from app.services.widget_service import answer_widget_message, list_widget_leads

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.post("/auth/login", response_model=LoginResponse)
def login_request(payload: LoginRequest):
    return login(payload)


@router.get("/system/status", response_model=SystemStatusResponse)
def system_status():
    return get_system_status()


@router.get("/trade-sources", response_model=TradeSourceStatusResponse)
def trade_sources():
    return list_trade_sources()


@router.get("/modules", response_model=list[ModuleInfo])
def get_modules():
    return list_modules()


@router.get("/subscription", response_model=SubscriptionPlan)
def get_subscription():
    return get_demo_plan()


@router.get("/customer/profile", response_model=CustomerProfile)
def get_profile():
    return get_customer_profile()


@router.post("/customer/profile", response_model=CustomerProfile)
def save_profile(payload: CustomerProfile):
    return save_customer_profile(payload)


@router.post("/subscription/reset-usage", response_model=SubscriptionPlan)
def reset_subscription_usage():
    return reset_query_usage()


@router.post("/access/check", response_model=AccessCheckResponse)
def check_module_access(payload: AccessCheckRequest):
    return check_access(payload)


@router.post("/searches", response_model=SearchResponse)
def create_search_request(payload: SearchRequest):
    return create_search(payload)


@router.post("/images/product", response_model=ImageUploadResponse)
def upload_product_image(file: UploadFile):
    return save_product_image(file)


@router.get("/searches/history", response_model=list[SearchHistoryItem])
def get_search_history():
    return list_search_history()


@router.post("/ai/keywords", response_model=KeywordPreview)
def preview_keywords(payload: SearchRequest):
    keywords = build_product_keywords(payload)
    return KeywordPreview(
        primary_terms=keywords.primary_terms,
        buyer_intents=keywords.buyer_intents,
        contact_roles=keywords.contact_roles,
    )


@router.post("/ai/dictionary/validate", response_model=DictionaryValidationResponse)
def validate_dictionary(payload: DictionaryValidationRequest):
    return validate_dictionary_terms(payload)


@router.post("/ai/dictionary/from-search", response_model=DictionaryValidationResponse)
def validate_dictionary_from_search(payload: SearchRequest):
    return validate_dictionary_terms(DictionaryValidationRequest(terms=terms_from_search_request(payload)))


@router.post("/campaigns/preview", response_model=CampaignPreview)
def preview_campaign(payload: CampaignPreviewRequest):
    return build_campaign_preview(payload)


@router.post("/campaigns/queue", response_model=CampaignJob)
def queue_campaign_request(payload: CampaignQueueRequest):
    return queue_campaign(payload.preview)


@router.get("/campaigns", response_model=list[CampaignJob])
def get_campaigns():
    return list_campaigns()


@router.post("/campaigns/{campaign_id}/send", response_model=CampaignJob)
def send_campaign_request(campaign_id: str):
    try:
        return send_campaign(campaign_id)
    except ValueError as exc:
        if str(exc) == "campaign_not_found":
            raise HTTPException(status_code=404, detail="Campaign not found") from exc
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/fairs/scan", response_model=FairScanResponse)
def scan_fair(payload: FairScanRequest):
    return scan_fair_participants(payload)


@router.post("/fairs/list-scan", response_model=FairScanResponse)
def scan_fair_manual_list(payload: FairListScanRequest):
    return scan_fair_list(payload)


@router.post("/chat/answer", response_model=ChatResponse)
def chat_answer(payload: ChatRequest):
    return answer_chat(payload)


@router.post("/rfq/scan", response_model=RfqScanResponse)
def scan_rfq(payload: RfqScanRequest):
    return scan_rfq_opportunities(payload)


@router.post("/demand-shares", response_model=DemandShareJob)
def create_demand_share(payload: DemandShareRequest):
    return queue_demand_share(payload)


@router.get("/demand-shares", response_model=list[DemandShareJob])
def get_demand_shares():
    return list_demand_shares()


@router.get("/training/lessons", response_model=list[TrainingLesson])
def get_training_lessons():
    return list_training_lessons()


@router.post("/training/quiz", response_model=TrainingQuizResult)
def post_training_quiz(payload: TrainingQuizSubmission):
    return submit_training_quiz(payload)


@router.get("/training/results", response_model=list[TrainingQuizResult])
def get_training_results():
    return list_training_results()


@router.post("/widget/message", response_model=WidgetMessageResponse)
def widget_message(payload: WidgetMessageRequest):
    return answer_widget_message(payload)


@router.get("/widget/leads", response_model=list[WidgetLeadRecord])
def widget_leads():
    return list_widget_leads()


@router.post("/visitors/consent", response_model=VisitorConsentResponse)
def save_visitor_consent(payload: VisitorConsent, request: Request):
    visitor = record_visitor(payload, fallback_ip=request.client.host if request.client else None)
    return VisitorConsentResponse(
        status="accepted" if payload.consent else "declined",
        next_step="geo_company_lookup" if payload.consent else "ip_lookup",
        visitor=visitor,
    )


@router.get("/visitors", response_model=list[VisitorRecord])
def get_visitors():
    return list_visitors()


@router.post("/exports/leads.xlsx")
def export_leads(payload: SearchResponse):
    excel_file = build_leads_excel(payload.results)
    headers = {"Content-Disposition": 'attachment; filename="potansiyel_musteriler.xlsx"'}
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


@router.post("/exports/fair-participants.xlsx")
def export_fair_participants(payload: FairScanResponse):
    excel_file = build_fair_participants_excel(payload.participants)
    headers = {"Content-Disposition": 'attachment; filename="fuar_katilimcilari.xlsx"'}
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


@router.get("/exports/operation-report.xlsx")
def export_operation_report():
    excel_file = build_operation_report_excel()
    headers = {"Content-Disposition": 'attachment; filename="operasyon_raporu.xlsx"'}
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )
