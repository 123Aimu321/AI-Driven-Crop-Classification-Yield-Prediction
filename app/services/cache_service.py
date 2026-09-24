import time
from typing import Any


class TTLCache:
    def __init__(self, ttl_seconds: int):
        self.ttl_seconds = ttl_seconds
        self._cache: dict[str, tuple[float, Any]] = {}

    def get(self, key: str):
        item = self._cache.get(key)

        if item is None:
            return None

        created_at, value = item

        if time.monotonic() - created_at > self.ttl_seconds:
            self._cache.pop(key, None)
            return None

        return value

    def set(self, key: str, value: Any):
        self._cache[key] = (
            time.monotonic(),
            value,
        )

    def delete(self, key: str):
        self._cache.pop(key, None)

    def clear(self):
        self._cache.clear()


# Location does not change frequently.
location_cache = TTLCache(
    ttl_seconds=3600
)

# Weather changes more frequently.
weather_cache = TTLCache(
    ttl_seconds=600
)

# Soil/environment data can be cached longer.
soil_cache = TTLCache(
    ttl_seconds=1800
)

# Historical annual rainfall can be cached for a day.
rainfall_cache = TTLCache(
    ttl_seconds=86400
)