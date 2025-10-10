from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
import time
import os

API_KEY = os.getenv("API_KEY")
RATE_LIMIT_RPS = int(os.getenv("RATE_LIMIT_RPS", "10"))
RATE_LIMIT_BURST = int(os.getenv("RATE_LIMIT_BURST", "20"))

_buckets = {}

class Bucket:
    def __init__(self, capacity: int, refill_per_sec: int):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_per_sec = refill_per_sec
        self.last = time.time()

    def allow(self) -> bool:
        now = time.time()
        elapsed = now - self.last
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_per_sec)
        self.last = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

def require_api_key(request: Request):
    if API_KEY:
        key = request.headers.get("x-api-key")
        if key != API_KEY:
            raise HTTPException(status_code=401, detail="Unauthorized")
    return True

def register_middlewares(app: FastAPI) -> None:
    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        if request.url.path in ("/health", "/docs", "/openapi.json"):
            return await call_next(request)
        ip = request.client.host if request.client else "unknown"
        b = _buckets.get(ip)
        if b is None:
            b = Bucket(RATE_LIMIT_BURST, RATE_LIMIT_RPS)
            _buckets[ip] = b
        if not b.allow():
            return PlainTextResponse(status_code=429, content="Rate limit exceeded")
        return await call_next(request)

    @app.middleware("http")
    async def request_logging(request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration_ms = int((time.time() - start) * 1000)
        print(f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)")
        return response

def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(status_code=exc.status_code, content={
            "error": {"type": "HTTPException", "detail": exc.detail, "path": request.url.path}
        })

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        print(f"ERROR {request.method} {request.url.path}: {exc}")
        return JSONResponse(status_code=500, content={
            "error": {"type": "ServerError", "detail": "An unexpected error occurred", "path": request.url.path}
        })

