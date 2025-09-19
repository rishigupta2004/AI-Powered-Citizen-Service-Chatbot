from fastapi import FastAPI
from backend.api.routers import health, services
from backend.api.middleware.logging import setup_logging

app = FastAPI(title="Citizen Services Chatbot API")

# include routers
app.include_router(health.router, prefix="/api")
app.include_router(services.router, prefix="/api/services")

# setup logging middleware
setup_logging(app)

@app.get("/")
def root():
    return {"message": "Citizen Services API is running"}
