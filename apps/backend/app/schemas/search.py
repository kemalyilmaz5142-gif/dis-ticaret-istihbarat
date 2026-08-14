from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    target_country: str = Field(..., examples=["Ingiltere"])
    country_domain: str | None = Field(default=None, examples=[".co.uk"])
    product_name_tr: str | None = None
    product_name_en: str | None = None
    product_name_es: str | None = None
    product_name_ru: str | None = None
    product_name_ar: str | None = None
    product_name_fr: str | None = None
    product_name_de: str | None = None
    extra_language_terms: dict[str, str] = Field(default_factory=dict)
    hs_code: str | None = None
    oem_no: str | None = None
    competitors: list[str] = Field(default_factory=list)
    related_sectors: list[str] = Field(default_factory=list)
    potential_customer_websites: list[str] = Field(default_factory=list)
    customer_product_terms: list[str] = Field(default_factory=list)
    excluded_product_terms: list[str] = Field(default_factory=list)
    market_strategy: str = "standard"
    simulate_search_location: bool = False
    location_provider: str | None = None
    search_engines: list[str] = Field(default_factory=lambda: ["google", "bing", "yandex"])
    search_all_countries: bool = False
    country_groups: list[str] = Field(default_factory=list)
    extra_target_countries: list[str] = Field(default_factory=list)
    trade_database_sources: list[str] = Field(default_factory=list)
    search_maps: bool = True
    search_web: bool = True
    product_image_id: str | None = None


class LeadResult(BaseModel):
    company_name: str
    country: str
    city: str | None = None
    address: str | None = None
    website: str | None = None
    email: str | None = None
    phone: str | None = None
    source: str
    source_type: str = "web"
    matched_keyword: str | None = None
    site_category: str = "unknown"
    site_category_reason: str | None = None
    score: int
    notes: str | None = None
    ai_fit_reason: str | None = None
    suggested_contact_role: str | None = None
    suggested_contact_emails: list[str] = Field(default_factory=list)
    suggested_email_subject: str | None = None
    suggested_email_body: str | None = None


class SearchQueryPlanItem(BaseModel):
    engine: str
    language: str
    query: str
    target_country: str
    country_domain: str | None = None
    source_type: str


class SearchResponse(BaseModel):
    request_id: str
    status: str
    query_plan: list[SearchQueryPlanItem] = Field(default_factory=list)
    results: list[LeadResult]


class SearchHistoryItem(BaseModel):
    request_id: str
    status: str
    target_country: str
    product_name: str | None = None
    result_count: int
    created_at: str


class KeywordPreview(BaseModel):
    primary_terms: list[str]
    buyer_intents: list[str]
    contact_roles: list[str]


class ImageUploadResponse(BaseModel):
    image_id: str
    filename: str
    content_type: str | None = None
    size_bytes: int
    sha256: str
    width: int | None = None
    height: int | None = None
    image_format: str | None = None
    average_color: str | None = None
    visual_signature: str | None = None
    status: str = "stored"
