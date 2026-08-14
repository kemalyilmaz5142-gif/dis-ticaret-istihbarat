import json
from pathlib import Path

from app.schemas.modules import AccessCheckRequest, AccessCheckResponse, ModuleInfo, SubscriptionPlan
from app.services.customer_service import get_customer_profile


MODULE_CATALOG = [
    ModuleInfo(
        code="lead_search",
        name="Potansiyel Müşteri Arama",
        description="Ürün, ülke, dil, rakip ve sektör bilgisine göre web, harita ve veritabanı kaynaklarından firma bulur.",
        setup_price_usd=2000,
        monthly_price_usd=30,
    ),
    ModuleInfo(
        code="maps_search",
        name="Harita Firma Arama",
        description="Haritalarda konumu olan firmaları kelime ve ülke bazlı tarar.",
        setup_price_usd=500,
        monthly_price_usd=10,
    ),
    ModuleInfo(
        code="contact_finder",
        name="Yetkili E-posta Bulma",
        description="Info e-posta yerine satın alma, ithalat veya yönetici kontaklarını bulmaya çalışır.",
        setup_price_usd=750,
        monthly_price_usd=20,
    ),
    ModuleInfo(
        code="email_outreach",
        name="Otomatik Mail Gönderimi",
        description="Excel listesindeki firmalara kontrollü tanıtım maili ve katalog gönderimi için hazırlık yapar.",
        setup_price_usd=1000,
        monthly_price_usd=40,
    ),
    ModuleInfo(
        code="fair_scan",
        name="Fuar Katılımcı Tarama",
        description="Fuar katılımcı listelerini hedef ürün ve sektör bilgisine göre eşleştirir.",
        setup_price_usd=1000,
        monthly_price_usd=25,
    ),
    ModuleInfo(
        code="chat_assistant",
        name="Web Chat Robotu",
        description="Panel kullanımı, firma önceliklendirme ve kampanya hazırlığı için yardımcı cevaplar üretir.",
        setup_price_usd=750,
        monthly_price_usd=20,
    ),
    ModuleInfo(
        code="market_strategy",
        name="Çin/ABD Özel Arama",
        description="Çin ve ABD pazarları için kaynak, domain ve niyet kelimelerini arama planına ekler.",
        setup_price_usd=1250,
        monthly_price_usd=35,
    ),
    ModuleInfo(
        code="visitor_identification",
        name="Web Ziyaretçi Tespiti",
        description="Web sitesini ziyaret eden firmaları konum/IP sinyalleriyle raporlamaya hazırlar.",
        setup_price_usd=1500,
        monthly_price_usd=30,
    ),
]


DEMO_PLAN = SubscriptionPlan(
    plan_code="demo_all_modules",
    customer_name="Demo Müşteri",
    enabled_modules=[module.code for module in MODULE_CATALOG],
    monthly_query_limit=500,
    used_queries=0,
)

STORAGE_DIR = Path(__file__).resolve().parents[2] / "storage"
USAGE_FILE = STORAGE_DIR / "subscription_usage.json"


def list_modules() -> list[ModuleInfo]:
    return MODULE_CATALOG


def get_demo_plan() -> SubscriptionPlan:
    usage = _read_usage()
    profile = get_customer_profile()
    return SubscriptionPlan(
        plan_code=DEMO_PLAN.plan_code,
        customer_name=profile.customer_name,
        enabled_modules=list(DEMO_PLAN.enabled_modules),
        monthly_query_limit=DEMO_PLAN.monthly_query_limit,
        used_queries=usage.get("used_queries", 0),
    )


def check_access(request: AccessCheckRequest) -> AccessCheckResponse:
    plan = get_demo_plan()

    if request.module_code not in {module.code for module in MODULE_CATALOG}:
        return AccessCheckResponse(
            allowed=False,
            module_code=request.module_code,
            reason="modül bulunamadı",
        )

    if request.module_code not in plan.enabled_modules:
        return AccessCheckResponse(
            allowed=False,
            module_code=request.module_code,
            reason="modül abonelikte aktif değil",
        )

    if plan.used_queries >= plan.monthly_query_limit:
        return AccessCheckResponse(
            allowed=False,
            module_code=request.module_code,
            reason="aylık sorgu limiti doldu",
        )

    return AccessCheckResponse(
        allowed=True,
        module_code=request.module_code,
        reason="erişim aktif",
    )


def increment_query_usage(amount: int = 1) -> SubscriptionPlan:
    plan = get_demo_plan()
    used_queries = min(plan.monthly_query_limit, plan.used_queries + max(0, amount))
    _write_usage({"used_queries": used_queries})
    return get_demo_plan()


def reset_query_usage() -> SubscriptionPlan:
    _write_usage({"used_queries": 0})
    return get_demo_plan()


def _read_usage() -> dict:
    if not USAGE_FILE.exists():
        return {"used_queries": 0}
    try:
        data = json.loads(USAGE_FILE.read_text(encoding="utf-8"))
        return {"used_queries": int(data.get("used_queries", 0))}
    except (json.JSONDecodeError, OSError, ValueError):
        return {"used_queries": 0}


def _write_usage(data: dict) -> None:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    USAGE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
