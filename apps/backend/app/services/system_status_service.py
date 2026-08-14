from app.core.config import get_settings
from app.schemas.system import IntegrationStatus, SystemStatusResponse


def get_system_status() -> SystemStatusResponse:
    settings = get_settings()
    return SystemStatusResponse(
        app_name=settings.app_name,
        app_env=settings.app_env,
        integrations=[
            _database_status(settings.database_url),
            _live_web_status(settings.enable_live_web_search),
            _serpapi_status(settings.serpapi_api_key),
            _ip_lookup_status(settings.enable_live_ip_lookup, settings.ipinfo_token),
            _smtp_status(
                settings.enable_email_sending,
                settings.smtp_host,
                settings.smtp_from_email,
            ),
            _location_simulation_status(
                settings.enable_location_simulation,
                settings.location_provider,
                settings.valentin_app_path,
            ),
            IntegrationStatus(
                code="trade_databases",
                name="Dis ticaret veritabanlari",
                status="ready" if settings.enabled_trade_sources else "planned",
                detail="Etkin kaynaklar: " + settings.enabled_trade_sources if settings.enabled_trade_sources else "Kaynak katalogu hazir; uyelik/API bilgileri bekleniyor.",
            ),
            IntegrationStatus(
                code="json_fallback",
                name="JSON yedek kayit",
                status="ready",
                detail="PostgreSQL hazir degilse profil, gecmis ve kuyruk kayitlari dosyada tutulur.",
            ),
        ],
    )


def _database_status(database_url: str) -> IntegrationStatus:
    configured = bool(database_url)
    return IntegrationStatus(
        code="postgresql",
        name="PostgreSQL",
        status="configured" if configured else "missing",
        detail="Baglanti adresi tanimli." if configured else "DATABASE_URL eksik.",
    )


def _live_web_status(enabled: bool) -> IntegrationStatus:
    return IntegrationStatus(
        code="live_web_search",
        name="Canli web arama",
        status="enabled" if enabled else "disabled",
        detail="DuckDuckGo HTML arama adaptoru acik." if enabled else "ENABLE_LIVE_WEB_SEARCH kapali.",
    )


def _serpapi_status(api_key: str) -> IntegrationStatus:
    return IntegrationStatus(
        code="serpapi_maps",
        name="SerpAPI harita",
        status="ready" if api_key else "missing",
        detail="SERPAPI_API_KEY tanimli." if api_key else "SERPAPI_API_KEY girilirse canli harita aramasi guclenir.",
    )


def _ip_lookup_status(enabled: bool, token: str) -> IntegrationStatus:
    if not enabled:
        return IntegrationStatus(
            code="ip_lookup",
            name="IP firma tespiti",
            status="disabled",
            detail="ENABLE_LIVE_IP_LOOKUP kapali.",
        )
    return IntegrationStatus(
        code="ip_lookup",
        name="IP firma tespiti",
        status="ready" if token else "basic",
        detail="IPINFO_TOKEN tanimli." if token else "Token yoksa temel ip-api denemesi kullanilir.",
    )


def _smtp_status(enabled: bool, host: str, from_email: str) -> IntegrationStatus:
    if not enabled:
        return IntegrationStatus(
            code="smtp",
            name="SMTP mail gonderimi",
            status="disabled",
            detail="Guvenli varsayilan: ENABLE_EMAIL_SENDING kapali.",
        )
    ready = bool(host and from_email)
    return IntegrationStatus(
        code="smtp",
        name="SMTP mail gonderimi",
        status="ready" if ready else "missing",
        detail="SMTP ayarlari tamam." if ready else "SMTP_HOST ve SMTP_FROM_EMAIL gerekli.",
    )


def _location_simulation_status(enabled: bool, provider: str, app_path: str) -> IntegrationStatus:
    if not enabled:
        return IntegrationStatus(
            code="location_simulation",
            name="Lokasyon simulasyonu",
            status="disabled",
            detail="ENABLE_LOCATION_SIMULATION kapali; sorgular yalnizca plan seviyesinde ulke hedefler.",
        )
    ready = bool(provider and (provider != "valentin_desktop" or app_path))
    return IntegrationStatus(
        code="location_simulation",
        name="Lokasyon simulasyonu",
        status="ready" if ready else "missing",
        detail="Valentin/Playwright lokasyon saglayicisi hazir." if ready else "VALENTIN_APP_PATH veya alternatif saglayici gerekli.",
    )
