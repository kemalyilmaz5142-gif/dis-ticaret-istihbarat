from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Dis Ticaret Istihbarat API"
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/trade_intelligence"
    frontend_origin: str = "http://localhost:3000"
    serpapi_api_key: str = ""
    enable_live_web_search: bool = True
    ipinfo_token: str = ""
    enable_live_ip_lookup: bool = True
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    enable_email_sending: bool = False
    email_batch_size: int = 20
    demo_username: str = "demo"
    demo_password: str = "demo123"
    enable_location_simulation: bool = False
    location_provider: str = "valentin_desktop"
    valentin_app_path: str = ""
    enabled_trade_sources: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
