import re
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse({"error": "Too many requests", "detail": str(exc)}, status_code=429)

INJECTION = re.compile(r'(ignore previous|forget instructions|jailbreak|system prompt|you are now|act as|DAN mode)', re.IGNORECASE)
SQL_INJECT = re.compile(r'(DROP\s+TABLE|SELECT\s+\*|UNION\s+SELECT|DELETE\s+FROM|INSERT\s+INTO|UPDATE\s+\w+\s+SET|--\s*$|;\s*--)', re.IGNORECASE)
XSS = re.compile(r'(<\s*script|javascript:|on\w+\s*=|alert\s*\()', re.IGNORECASE)
MAX_MSG_LEN = 2000

def sanitize_input(text: str) -> tuple[str, bool]:
    if not text or not text.strip():
        return "", False
    if len(text) > MAX_MSG_LEN:
        text = text[:MAX_MSG_LEN]
    if INJECTION.search(text): return text, False
    if SQL_INJECT.search(text): return text, False
    if XSS.search(text): return text, False
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip(), True
