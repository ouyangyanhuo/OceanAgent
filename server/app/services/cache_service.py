import hashlib
import time
from typing import Any

from app.core.config import get_settings
from app.core.json_store import read_json, write_json
from app.core.paths import AGENT_CACHE_FILE, AI_CACHE_FILE, REPORT_CACHE_FILE


class CacheService:
    cache_files = {
        "ai": AI_CACHE_FILE,
        "report": REPORT_CACHE_FILE,
        "agent": AGENT_CACHE_FILE,
    }

    def make_key(self, *parts: Any) -> str:
        raw = "|".join(str(part) for part in parts)
        return hashlib.md5(raw.encode("utf-8")).hexdigest()

    def get(self, cache_name: str, key: str) -> dict[str, Any] | None:
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
        data = read_json(self.cache_files[cache_name], {})
        data.pop(key, None)
        write_json(self.cache_files[cache_name], data)

    def clear(self, cache_name: str | None = None) -> None:
        names = [cache_name] if cache_name else list(self.cache_files)
        for name in names:
            write_json(self.cache_files[name], {})

    def status(self) -> dict[str, Any]:
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
        return cache_exists and not expired and hit_rate > 0
