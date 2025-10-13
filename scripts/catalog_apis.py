#!/usr/bin/env python3
"""Discover and catalog API endpoints (ONLY_DISCOVER). No live calls.
Output: artifacts/api_catalog.json
"""
import json

CATALOG = {
    "passport": {
        "provider": "APISetu",
        "base": "https://apisetu.gov.in/passport",
        "endpoints": [
            {"path": "/psk/locate", "params": ["pin", "city"], "auth": "api-key", "rate_limit": "tbd", "sla": "tbd"},
            {"path": "/fees/calculate", "params": ["serviceType"], "auth": "api-key", "rate_limit": "tbd", "sla": "tbd"}
        ]
    },
    "aadhaar": {
        "provider": "UIDAI",
        "base": "https://uidai.gov.in/api",
        "endpoints": [
            {"path": "/ekyc", "params": ["aadhaar"], "auth": "otp+api-key", "rate_limit": "tbd", "sla": "tbd"}
        ]
    },
    "pan": {
        "provider": "CBDT",
        "base": "https://incometax.gov.in/api",
        "endpoints": [
            {"path": "/pan/verify", "params": ["pan"], "auth": "api-key", "rate_limit": "tbd", "sla": "tbd"}
        ]
    },
}

print(json.dumps(CATALOG, indent=2))


