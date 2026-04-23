"""Clerk session sync endpoint for local auth session issuance."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Optional, cast

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.auth_models import AuthMethod, User, UserAuthMethod, UserSession
from core.config import (
    CLERK_BACKEND_API_URL,
    CLERK_FRONTEND_API_URL,
    CLERK_DOMAIN,
    CLERK_JWKS_URL,
    CLERK_SECRET_KEY,
)
from core.database import get_db
from routes.auth_endpoints import AuthResponse, create_user_session

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth/clerk", tags=["Clerk Auth"])

_jwks_cache: Optional[dict[str, Any]] = None


class ClerkSyncRequest(BaseModel):
    clerk_token: str


async def _fetch_jwks() -> dict[str, Any]:
    global _jwks_cache
    if _jwks_cache is not None:
        return cast(dict[str, Any], _jwks_cache)
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(CLERK_JWKS_URL)
        resp.raise_for_status()
        payload = resp.json()
        _jwks_cache = payload if isinstance(payload, dict) else {}
        return _jwks_cache


async def _verify_clerk_token(token: str) -> dict[str, Any]:
    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        jwks = await _fetch_jwks()
        rsa_key = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)

        if not rsa_key:
            global _jwks_cache
            _jwks_cache = None
            jwks = await _fetch_jwks()
            rsa_key = next(
                (k for k in jwks.get("keys", []) if k.get("kid") == kid), None
            )

        if not rsa_key:
            raise HTTPException(status_code=401, detail="Clerk signing key not found")

        claims = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
        expected_issuers = {
            value.rstrip("/")
            for value in [CLERK_FRONTEND_API_URL, CLERK_DOMAIN]
            if value
        }
        issuer = str(claims.get("iss") or "").rstrip("/")
        if expected_issuers and issuer and issuer not in expected_issuers:
            raise HTTPException(status_code=401, detail="Invalid Clerk token issuer")
        return claims
    except JWTError as exc:
        logger.warning("Clerk JWT verification failed: %s", exc)
        raise HTTPException(status_code=401, detail=f"Invalid Clerk token: {exc}")


async def _fetch_clerk_user_profile(clerk_user_id: str) -> dict[str, Any]:
    if not CLERK_SECRET_KEY or not clerk_user_id:
        return {}
    endpoint = f"{CLERK_BACKEND_API_URL.rstrip('/')}/v1/users/{clerk_user_id}"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                endpoint,
                headers={
                    "Authorization": f"Bearer {CLERK_SECRET_KEY}",
                    "Content-Type": "application/json",
                },
            )
            if resp.status_code >= 400:
                logger.warning(
                    "Clerk profile fetch failed for %s with status %s",
                    clerk_user_id,
                    resp.status_code,
                )
                return {}
            payload = resp.json()
            if not isinstance(payload, dict):
                return {}
            return payload
    except Exception as exc:
        logger.warning("Clerk profile fetch error for %s: %s", clerk_user_id, exc)
        return {}


def _extract_primary_contact(
    profile: dict[str, Any], key: str, primary_id_key: str
) -> str | None:
    entries = profile.get(key)
    if not isinstance(entries, list):
        return None
    primary_id = profile.get(primary_id_key)
    selected = None
    if primary_id:
        selected = next(
            (item for item in entries if item.get("id") == primary_id), None
        )
    if not selected and entries:
        selected = entries[0]
    if not isinstance(selected, dict):
        return None
    value = selected.get("email_address") or selected.get("phone_number")
    return value if isinstance(value, str) and value else None


def _clerk_strategy_to_auth_method(claims: dict[str, Any]) -> AuthMethod:
    ext_accounts = claims.get("external_accounts", [])
    for acc in ext_accounts:
        if acc.get("provider") in ("google", "google.com", "oauth_google"):
            return AuthMethod.CLERK_GOOGLE
    if claims.get("phone_number") and not claims.get("email"):
        return AuthMethod.CLERK_PHONE
    return AuthMethod.CLERK


@router.post("/sync", response_model=AuthResponse)
async def clerk_sync(
    payload: ClerkSyncRequest,
    req: Request,
    db: Session = Depends(get_db),
):
    if not CLERK_JWKS_URL:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Clerk backend sync is disabled. Set CLERK_JWKS_URL "
                f"(backend API: {CLERK_BACKEND_API_URL})."
            ),
        )

    claims = await _verify_clerk_token(payload.clerk_token)

    clerk_user_id: str = claims.get("sub", "")
    profile = await _fetch_clerk_user_profile(clerk_user_id)

    email: Optional[str] = claims.get("email") or claims.get("email_address")
    if not email:
        email = _extract_primary_contact(
            profile,
            "email_addresses",
            "primary_email_address_id",
        )

    phone: Optional[str] = claims.get("phone_number")
    if not phone:
        phone = _extract_primary_contact(
            profile,
            "phone_numbers",
            "primary_phone_number_id",
        )

    first_name: str = (
        claims.get("given_name")
        or claims.get("first_name")
        or str(profile.get("first_name") or "")
        or "User"
    )
    last_name: str = (
        claims.get("family_name")
        or claims.get("last_name")
        or str(profile.get("last_name") or "")
        or ""
    )
    full_name: str = f"{first_name} {last_name}".strip()
    is_verified: bool = bool(
        claims.get("email_verified") or claims.get("phone_verified")
    )
    if not is_verified and profile:
        is_verified = bool(
            profile.get("email_addresses") or profile.get("phone_numbers")
        )

    if not email and not phone:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Clerk token must contain at least an email or phone number.",
        )

    auth_method_type = _clerk_strategy_to_auth_method(claims)

    user: Optional[User] = None
    if email:
        user = db.query(User).filter(User.email == email).first()
    if not user and phone:
        user = db.query(User).filter(User.phone == phone).first()

    if not user:
        user = User(
            email=email,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            full_name=full_name,
            is_verified=is_verified,
            password_hash=None,
        )
        db.add(user)
        db.flush()
    else:
        if not user.full_name or user.full_name == "User":
            user.first_name = first_name
            user.last_name = last_name
            user.full_name = full_name
        if not user.is_verified and is_verified:
            user.is_verified = True
        user.last_login = datetime.utcnow()

    existing_method = (
        db.query(UserAuthMethod)
        .filter(
            UserAuthMethod.user_id == user.id,
            UserAuthMethod.provider_id == clerk_user_id,
        )
        .first()
    )
    provider_payload = json.dumps(
        {
            "clerk_user_id": clerk_user_id,
            "strategy": auth_method_type.value,
            "email": email,
            "phone": phone,
            "claims_sub": claims.get("sub"),
        }
    )
    if not existing_method:
        db.add(
            UserAuthMethod(
                user_id=user.id,
                method=auth_method_type,
                provider_id=clerk_user_id,
                provider_data=provider_payload,
            )
        )
    else:
        existing_method.last_used = datetime.utcnow()
        existing_method.provider_data = provider_payload

    db.commit()
    db.refresh(user)

    session: UserSession = create_user_session(db, user.id, req)

    return AuthResponse(
        access_token=session.session_token,
        refresh_token=session.refresh_token,
        expires_in=86400,
        user={
            "id": user.id,
            "uuid": user.uuid,
            "email": user.email,
            "phone": user.phone,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "is_verified": user.is_verified,
            "role": user.role.value,
        },
    )
