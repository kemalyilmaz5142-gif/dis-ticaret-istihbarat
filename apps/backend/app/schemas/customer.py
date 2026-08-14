from pydantic import BaseModel, Field


class CustomerProfile(BaseModel):
    customer_name: str = "Demo Musteri"
    company_name: str = "Demo Export Company"
    website: str | None = None
    catalog_url: str | None = None
    default_sender_email: str | None = None
    target_sector: str | None = None
    potential_customer_websites: list[str] = Field(default_factory=list)
    customer_product_terms: list[str] = Field(default_factory=list)
    excluded_product_terms: list[str] = Field(default_factory=list)
