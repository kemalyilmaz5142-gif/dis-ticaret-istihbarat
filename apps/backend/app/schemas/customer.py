from pydantic import BaseModel, Field


class ProfileProduct(BaseModel):
    name_tr: str = ""
    name_en: str = ""
    hs_code: str = ""
    image_url: str | None = None
    image_id: str | None = None
    image_filename: str | None = None


class CustomerProfile(BaseModel):
    customer_name: str = ""
    company_name: str = ""
    website: str | None = None
    catalog_url: str | None = None
    default_sender_email: str | None = None
    target_sector: str | None = None
    profile_products: list[ProfileProduct] = Field(default_factory=list)
    reference_websites: list[str] = Field(default_factory=list)
    potential_customer_websites: list[str] = Field(default_factory=list)
    customer_product_terms: list[str] = Field(default_factory=list)
    excluded_product_terms: list[str] = Field(default_factory=list)
