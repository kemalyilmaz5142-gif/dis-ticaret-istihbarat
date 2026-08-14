from pydantic import BaseModel, Field


class TradeSourceInfo(BaseModel):
    code: str
    name: str
    status: str
    detail: str
    source_type: str = "trade_database"


class TradeSourceStatusResponse(BaseModel):
    sources: list[TradeSourceInfo] = Field(default_factory=list)
