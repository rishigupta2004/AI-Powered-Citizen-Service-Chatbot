import time
from fastapi import Request

def setup_logging(app):
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        print(f"➡️ {request.method} {request.url.path} completed in {process_time:.2f} ms")
        return response
