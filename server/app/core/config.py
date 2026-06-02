from functools import lru_cache
from os import getenv

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = getenv("APP_NAME", "Ocean KG Agent")
    app_env: str = getenv("APP_ENV", "development")
    api_prefix: str = getenv("API_PREFIX", "/api")
    version: str = "0.1.0"
    cors_origins: list[str] = [
        origin.strip()
        for origin in getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    ]

    llm_provider: str = getenv("LLM_PROVIDER", "mock")
    llm_api_key: str = getenv("LLM_API_KEY", "")
    llm_base_url: str = getenv("LLM_BASE_URL", "")
    llm_model: str = getenv("LLM_MODEL", "")

    graph_expand_temperature: float = float(getenv("GRAPH_EXPAND_TEMPERATURE", "0.2"))
    report_temperature: float = float(getenv("REPORT_TEMPERATURE", "0.5"))

    cache_enabled: bool = getenv("CACHE_ENABLED", "true").lower() == "true"
    cache_hit_rate: float = float(getenv("CACHE_HIT_RATE", "0.75"))
    cache_ttl_seconds: int = int(getenv("CACHE_TTL_SECONDS", "86400"))

    allow_llm_graph_seed: bool = getenv("ALLOW_LLM_GRAPH_SEED", "true").lower() == "true"
    allow_llm_graph_expand: bool = getenv("ALLOW_LLM_GRAPH_EXPAND", "true").lower() == "true"

    @property
    def use_mock_llm(self) -> bool:
        return self.llm_provider == "mock" or not self.llm_api_key


@lru_cache
def get_settings() -> Settings:
    return Settings()
