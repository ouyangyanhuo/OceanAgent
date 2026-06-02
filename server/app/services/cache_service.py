"""JSON 文件缓存服务。

缓存用于 AI 回答、智能体结果和报告等表达层数据。
图谱结构扩展由 expansion_index.json 管理，不走概率缓存。
"""

import hashlib
import time
from typing import Any

from app.core.config import get_settings
from app.core.json_store import read_json, write_json
from app.core.paths import AGENT_CACHE_FILE, AI_CACHE_FILE, REPORT_CACHE_FILE


class CacheService:
    """封装缓存 key、读写、清空和状态查询。"""

    # 缓存名称到文件路径的映射，API 层也使用这些名称。
    cache_files = {
        "ai": AI_CACHE_FILE,
        "report": REPORT_CACHE_FILE,
        "agent": AGENT_CACHE_FILE,
    }

    def make_key(self, *parts: Any) -> str:
        """根据多个上下文片段生成稳定缓存 key。"""
        raw = "|".join(str(part) for part in parts)
        return hashlib.md5(raw.encode("utf-8")).hexdigest()

    def get(self, cache_name: str, key: str) -> dict[str, Any] | None:
        """读取缓存值。

        缓存不存在或已过期时返回 None。
        """
        data = read_json(self.cache_files[cache_name], {})
        item = data.get(key)
        if not item:
            return None
        expires_at = item.get("expires_at")
        if expires_at and expires_at < time.time():
            return None
        return item.get("value")

    def set(
        self,
        cache_name: str,
        key: str,
        value: dict[str, Any],
        ttl_seconds: int | None = None,
    ) -> None:
        """写入缓存值。

        ttl_seconds 为空时使用全局默认 TTL；ttl 为 0/None 表示不设置过期时间。
        """
        settings = get_settings()
        ttl = ttl_seconds if ttl_seconds is not None else settings.cache_ttl_seconds
        data = read_json(self.cache_files[cache_name], {})
        data[key] = {
            "value": value,
            "created_at": time.time(),
            "expires_at": time.time() + ttl if ttl else None,
        }
        write_json(self.cache_files[cache_name], data)

    def delete(self, cache_name: str, key: str) -> None:
        """删除指定缓存项。"""
        data = read_json(self.cache_files[cache_name], {})
        data.pop(key, None)
        write_json(self.cache_files[cache_name], data)

    def clear(self, cache_name: str | None = None) -> None:
        """清空指定缓存文件；未指定时清空全部缓存。"""
        names = [cache_name] if cache_name else list(self.cache_files)
        for name in names:
            write_json(self.cache_files[name], {})

    def status(self) -> dict[str, Any]:
        """返回缓存文件状态，供 /api/cache/status 使用。"""
        result = {}
        for name, path in self.cache_files.items():
            data = read_json(path, {})
            result[name] = {
                "path": str(path),
                "entries": len(data),
                "exists": path.exists(),
            }
        return result

    def should_use_cache(self, cache_exists: bool, expired: bool, hit_rate: float) -> bool:
        """判断是否使用缓存。

        当前调用路径主要直接使用 get()，该方法保留给后续概率缓存策略。
        """
        return cache_exists and not expired and hit_rate > 0
