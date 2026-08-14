from app.schemas.chat import ChatRequest, ChatResponse, ChatSuggestion
from app.schemas.modules import AccessCheckRequest
from app.schemas.search import LeadResult
from app.services.module_service import check_access


def answer_chat(request: ChatRequest) -> ChatResponse:
    access = check_access(AccessCheckRequest(module_code="chat_assistant"))
    if not access.allowed:
        return ChatResponse(reply="Chat modulu bu abonelikte aktif degil.", status="blocked")

    message = request.message.lower()
    if _asks_about_email(message):
        return _email_answer(request.current_results)
    if _asks_about_best_leads(message):
        return _best_leads_answer(request.current_results)
    if _asks_about_export(message):
        return ChatResponse(
            reply="Sonuc tablosunda Excel indir dugmesini kullanarak firma listesini Excel olarak alabilirsiniz.",
            suggestions=[
                ChatSuggestion(title="Excel kolonlari", detail="Firma, ulke, kaynak, iletisim, AI notu ve puan alanlari hazirlanir."),
            ],
        )
    if _asks_about_fair(message):
        return ChatResponse(
            reply="Fuar katilimci tarama panelinde fuar adi, ulke, urun ve sektor girerek katilimci adaylarini uretebilirsiniz.",
            suggestions=[
                ChatSuggestion(title="Iyi arama", detail="Urun adini Ingilizce, sektoru de daraltici ifade olarak yazin."),
            ],
        )

    return ChatResponse(
        reply=(
            "Bu panelde hedef ulke ve urun bilgisiyle firma arayabilir, sonuc listesini Excel'e aktarabilir, "
            "mail kampanyasi onizlemesi olusturabilir ve fuar katilimcisi tarayabilirsiniz."
        ),
        suggestions=_general_suggestions(request.current_results),
    )


def _email_answer(results: list[LeadResult]) -> ChatResponse:
    ready = [lead for lead in results if lead.suggested_contact_emails or lead.email]
    if not ready:
        return ChatResponse(
            reply="Su an mail icin hazir alici bulunmuyor. Once arama yapin veya firma web sitesi/e-posta bilgisi olan sonuclari toplayin.",
            suggestions=[ChatSuggestion(title="Sonraki adim", detail="Arama formunda urun ve hedef ulkeyi doldurup yeni arama baslatin.")],
        )

    top = sorted(ready, key=lambda lead: lead.score, reverse=True)[:3]
    names = ", ".join(lead.company_name for lead in top)
    return ChatResponse(
        reply=f"Mail kampanyasi icin en uygun ilk adaylar: {names}. Onizleme dugmesiyle alici listesini ve spam riskini kontrol edin.",
        suggestions=[
            ChatSuggestion(title="Kucuk parti", detail="Ilk gonderimde 20-25 alicilik kucuk bir parti tercih edin."),
            ChatSuggestion(title="Konu kontrolu", detail="Konu satirinda urun ve ihracat deger onerisi net olsun."),
        ],
    )


def _best_leads_answer(results: list[LeadResult]) -> ChatResponse:
    if not results:
        return ChatResponse(reply="Henuz sonuc yok. Once potansiyel musteri aramasi baslatin.")

    top = sorted(results, key=lambda lead: lead.score, reverse=True)[:5]
    lines = [f"{lead.company_name} ({lead.country}, puan {lead.score})" for lead in top]
    return ChatResponse(
        reply="En guclu adaylar: " + "; ".join(lines),
        suggestions=[
            ChatSuggestion(title="Oncelik", detail="Puan 75 ustu olanlari ilk temas listesine alin."),
            ChatSuggestion(title="Dogrulama", detail="Web sitesi ve e-posta olan firmalari once kontrol edin."),
        ],
    )


def _general_suggestions(results: list[LeadResult]) -> list[ChatSuggestion]:
    if results:
        return [
            ChatSuggestion(title="Sonuclari sirala", detail="Yuksek puanli ve e-posta adayi olan firmalari onceleyin."),
            ChatSuggestion(title="Mail hazirla", detail="Mail kampanyasi onizlemesiyle konu, alici ve spam riskini kontrol edin."),
        ]
    return [
        ChatSuggestion(title="Arama baslat", detail="Hedef ulke, urun adi ve sektor bilgisiyle ilk listeyi olusturun."),
        ChatSuggestion(title="Fuar tara", detail="Belirli bir fuar varsa katilimci tarama panelini kullanin."),
    ]


def _asks_about_email(message: str) -> bool:
    return any(word in message for word in ["mail", "email", "e-posta", "kampanya", "gonder"])


def _asks_about_best_leads(message: str) -> bool:
    return any(word in message for word in ["en iyi", "oncelik", "puan", "hangi firma", "aday"])


def _asks_about_export(message: str) -> bool:
    return any(word in message for word in ["excel", "indir", "cikti", "rapor"])


def _asks_about_fair(message: str) -> bool:
    return any(word in message for word in ["fuar", "katilimci", "stand"])
