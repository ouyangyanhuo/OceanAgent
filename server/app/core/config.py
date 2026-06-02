"""应用配置模块。

所有配置都从环境变量读取，并提供开发环境默认值。
这里暂时不依赖 pydantic-settings，是为了保持第一版后端轻量。
"""

from functools import lru_cache
from os import getenv

from pydantic import BaseModel


class Settings(BaseModel):
    """后端运行配置。

    字段命名使用 Python 风格，环境变量使用大写下划线风格。
    这些配置会被 FastAPI 入口、缓存服务和未来 LLM provider 复用。
    """

    # 应用基础信息和 API 前缀。
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

    # LLM provider 配置。当前实现保持 mock 模式可运行，真实 provider 后续接入。
    llm_provider: str = getenv("LLM_PROVIDER", "mock")
    llm_api_key: str = getenv("LLM_API_KEY", "")
    llm_base_url: str = getenv("LLM_BASE_URL", "")
    llm_model: str = getenv("LLM_MODEL", "")

    # 不同生成任务的温度配置，预留给真实 LLM 请求使用。
    graph_expand_temperature: float = float(getenv("GRAPH_EXPAND_TEMPERATURE", "0.2"))
    report_temperature: float = float(getenv("REPORT_TEMPERATURE", "0.5"))

    # 智能体回答和报告缓存配置；图谱结构扩展不走概率缓存。
    cache_enabled: bool = getenv("CACHE_ENABLED", "true").lower() == "true"
    cache_hit_rate: float = float(getenv("CACHE_HIT_RATE", "0.75"))
    cache_ttl_seconds: int = int(getenv("CACHE_TTL_SECONDS", "86400"))

    # 是否允许通过 LLM 生成图谱种子和扩展候选数据。
    allow_llm_graph_seed: bool = getenv("ALLOW_LLM_GRAPH_SEED", "true").lower() == "true"
    allow_llm_graph_expand: bool = getenv("ALLOW_LLM_GRAPH_EXPAND", "true").lower() == "true"

    @property
    def use_mock_llm(self) -> bool:
        """判断当前是否应使用 mock LLM。

        没有 API Key 时必须自动退回 mock，保证本地 demo 可以直接启动。
        """
        return self.llm_provider == "mock" or not self.llm_api_key


@lru_cache
def get_settings() -> Settings:
    """返回全局配置单例。

    使用 lru_cache 避免每次请求都重新解析环境变量。
    """
    return Settings()
