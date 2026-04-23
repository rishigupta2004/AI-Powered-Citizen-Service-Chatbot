from fastapi import APIRouter
from typing import Dict, List
import csv
import os

router = APIRouter(prefix="/api", tags=["Service API Endpoints"])

def _slugify(name: str) -> str:
    return (
        name.lower()
        .replace("/", "-")
        .replace("(", "")
        .replace(")", "")
        .replace(" ", "-")
        .replace("--", "-")
    )

def load_service_endpoints(csv_path: str) -> Dict[str, List[Dict[str, str]]]:
    data: Dict[str, List[Dict[str, str]]] = {}
    if not os.path.exists(csv_path):
        return data
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        current_service = None
        for row in reader:
            service = row.get("Service") or current_service or "Unknown"
            current_service = service if row.get("Service") else current_service
            api_service = row.get("API Service") or ""
            endpoint = row.get("Endpoint") or ""
            key = _slugify(service)
            lst = data.setdefault(key, [])
            # Leave link empty per requirement
            lst.append({
                "service": service,
                "api_service": api_service,
                "endpoint_name": endpoint.split("/")[-1] if endpoint else "",
                "link": ""
            })
    return data

CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Service-APIService-Endpoint.csv")
_ENDPOINTS = load_service_endpoints(CSV_PATH)

@router.get("/service-endpoints")
def list_services() -> List[str]:
    return sorted(list(_ENDPOINTS.keys()))

@router.get("/service-endpoints/{service_slug}")
def list_service_endpoints(service_slug: str) -> List[Dict[str, str]]:
    return _ENDPOINTS.get(service_slug, [])