"""
In-memory LRU response cache for chat queries.
Cuts repeat query latency from ~5000ms → <50ms.
"""
from collections import OrderedDict
from hashlib import md5
import time

class ResponseCache:
    def __init__(self, max_size=500, ttl_seconds=3600):
        self._cache: OrderedDict = OrderedDict()
        self._max_size = max_size
        self._ttl = ttl_seconds
        self._hits = 0
        self._misses = 0

    def _key(self, message: str, language: str) -> str:
        return md5(f"{message.lower().strip()}:{language}".encode()).hexdigest()

    def get(self, message: str, language: str):
        key = self._key(message, language)
        if key in self._cache:
            entry, ts = self._cache[key]
            if time.time() - ts < self._ttl:
                self._cache.move_to_end(key)
                self._hits += 1
                return entry
            del self._cache[key]
        self._misses += 1
        return None

    def set(self, message: str, language: str, response: dict):
        key = self._key(message, language)
        self._cache[key] = (response, time.time())
        self._cache.move_to_end(key)
        if len(self._cache) > self._max_size:
            self._cache.popitem(last=False)

    @property
    def stats(self):
        return {"hits": self._hits, "misses": self._misses, "size": len(self._cache),
                "hit_rate": f"{100*self._hits//(self._hits+self._misses+1)}%"}

chat_cache = ResponseCache(max_size=500, ttl_seconds=3600)

def ttl_cache(ttl_seconds=3600, max_size=100):
    """Decorator factory for simple TTL caching."""
    def decorator(func):
        _cache = {}
        def wrapper(*args, **kwargs):
            from hashlib import md5
            import time
            key = md5(str(args).encode()).hexdigest()
            if key in _cache:
                result, ts = _cache[key]
                if time.time() - ts < ttl_seconds:
                    return result
            result = func(*args, **kwargs)
            _cache[key] = (result, time.time())
            return result
        return wrapper
    return decorator
