import time
from typing import Any, Callable, Dict, Tuple


_CACHE_STORE: Dict[str, Tuple[float, Any]] = {}


def ttl_cache(ttl_seconds: int = 60) -> Callable:
    """
    Simple in-memory TTL cache for pure GET handlers.
    Keyed by function name and args/kwargs representation.
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{sorted(kwargs.items())}"
            now = time.time()
            if key in _CACHE_STORE:
                ts, value = _CACHE_STORE[key]
                if now - ts < ttl_seconds:
                    return value
            result = func(*args, **kwargs)
            _CACHE_STORE[key] = (now, result)
            return result

        return wrapper

    return decorator