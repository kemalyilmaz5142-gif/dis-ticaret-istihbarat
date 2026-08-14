from pydantic import BaseModel, Field


class ModuleInfo(BaseModel):
    code: str
    name: str
    description: str
    setup_price_usd: int
    monthly_price_usd: int
    enabled: bool = True


class SubscriptionPlan(BaseModel):
    plan_code: str
    customer_name: str
    enabled_modules: list[str] = Field(default_factory=list)
    monthly_query_limit: int
    used_queries: int


class AccessCheckRequest(BaseModel):
    module_code: str
    customer_name: str = "Demo Musteri"


class AccessCheckResponse(BaseModel):
    allowed: bool
    module_code: str
    reason: str

