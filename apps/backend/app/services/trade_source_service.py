from app.core.config import get_settings
from app.schemas.trade_sources import TradeSourceInfo, TradeSourceStatusResponse


TRADE_SOURCE_CATALOG = [
    ("tradeatlas", "TradeAtlas"),
    ("importgenius", "ImportGenius"),
    ("trademo", "Trademo Intel"),
    ("panjiva", "Panjiva"),
    ("global_buyers_online", "Global Buyers Online"),
    ("europages", "Europages"),
    ("tradekey", "TradeKey"),
    ("trademap", "TradeMap"),
    ("oneworld_yellow_pages", "Oneworld Yellow Pages"),
    ("vujis", "Vujis"),
    ("apify", "Apify"),
    ("exim_data", "Exim Data"),
    ("tradecalculus_ai", "TradecalculusAI"),
    ("un_comtrade", "UN Comtrade"),
    ("kompass", "Kompass"),
]


def list_trade_sources() -> TradeSourceStatusResponse:
    settings = get_settings()
    ready_sources = {item.strip() for item in settings.enabled_trade_sources.split(",") if item.strip()}
    return TradeSourceStatusResponse(
        sources=[
            TradeSourceInfo(
                code=code,
                name=name,
                status="ready" if code in ready_sources else "planned",
                detail=(
                    "Canli adaptor icin etkinlestirildi."
                    if code in ready_sources
                    else "API/uyelik bilgisi eklenince canli veri toplanacak."
                ),
            )
            for code, name in TRADE_SOURCE_CATALOG
        ]
    )


def selected_trade_sources(request_sources: list[str]) -> list[tuple[str, str]]:
    allowed = dict(TRADE_SOURCE_CATALOG)
    selected = [code for code in request_sources if code in allowed]
    if not selected:
        selected = ["europages", "kompass", "un_comtrade", "tradeatlas", "panjiva"]
    return [(code, allowed[code]) for code in selected[:8]]
