from app.schemas.rfq import RfqOpportunity, RfqScanRequest, RfqScanResponse


RFQ_PLATFORMS = {
    "tradekey": "TradeKey",
    "ecplaza": "ECPlaza",
    "eworldtrade": "eWorldTrade",
    "indiamart": "IndiaMART",
    "tradeindia": "TradeIndia",
    "made_in_china": "Made-in-China",
    "dhgate": "DHgate",
    "ec21": "EC21",
    "thomasnet": "Thomasnet",
}


def scan_rfq_opportunities(request: RfqScanRequest) -> RfqScanResponse:
    selected = [code for code in request.platforms if code in RFQ_PLATFORMS] or list(RFQ_PLATFORMS)[:5]
    opportunities = [
        _opportunity_for(request, code, index)
        for index, code in enumerate(selected[:9], start=1)
    ]
    return RfqScanResponse(opportunities=opportunities)


def _opportunity_for(request: RfqScanRequest, code: str, index: int) -> RfqOpportunity:
    platform = RFQ_PLATFORMS[code]
    country = request.target_country or ("United States" if code == "thomasnet" else "Global")
    keyword = request.hs_code or request.product_name
    return RfqOpportunity(
        platform=platform,
        title=f"RFQ candidate for {request.product_name}",
        buyer_country=country,
        quantity_hint=f"{index * 100} pcs or distributor inquiry",
        contact_hint="Buyer contact visible after platform login/API access",
        score=max(50, 88 - index * 4),
        source_url=f"https://{code}.example.com/rfq/{keyword.replace(' ', '-')}",
        notes="Talep avi adaptor yeri. Canli RFQ, uyelik veya API bilgisi eklenince bu kayit gercek taleple degisecek.",
    )
