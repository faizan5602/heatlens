import hashlib
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
from backend.config import settings


class JSONCacheService:
    def __init__(self, cache_dir: Path = settings.CACHE_DIR, ttl_seconds: int = settings.CACHE_TTL_SECONDS):
        self.cache_dir = cache_dir
        self.ttl = ttl_seconds

    def _generate_key(self, endpoint: str, method: str, payload: Dict[str, Any]) -> str:
        payload_str = json.dumps(payload, sort_keys=True)
        raw_key = f"{method.upper()}:{endpoint}:{payload_str}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    def get(self, endpoint: str, method: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        key = self._generate_key(endpoint, method, payload)
        file_path = self.cache_dir / f"{key}.json"

        if not file_path.exists():
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                cached = json.load(f)

            if time.time() - cached.get("_cached_at", 0) > self.ttl:
                file_path.unlink(missing_ok=True)
                return None

            return cached.get("data")
        except Exception:
            file_path.unlink(missing_ok=True)
            return None

    def set(self, endpoint: str, method: str, payload: Dict[str, Any], data: Dict[str, Any]) -> None:
        key = self._generate_key(endpoint, method, payload)
        file_path = self.cache_dir / f"{key}.json"

        wrapped = {
            "_cached_at": time.time(),
            "data": data,
        }
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(wrapped, f, indent=2)
        except Exception as e:
            print(f"[Cache Write Error] Failed writing {key}: {e}")


cache_service = JSONCacheService()
