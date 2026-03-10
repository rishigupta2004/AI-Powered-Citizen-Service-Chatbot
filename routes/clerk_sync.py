"""Clerk session sync endpoint for local auth session issuance."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.auth_models import AuthMethod, User, UserAuthMethod, UserSession
from core.config import CLERK_BACKEND_API_URL, CLERK_JWKS_URL, CLERK_SECRET_KEY
from core.database import get_db
from routes.auth_endpoints import AuthResponse, create_user_session

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth/clerk", tags=["Clerk Auth"])

_jwks_cache: Optional[dict[str, Any]] = None


class ClerkSyncRequest(BaseModel):
    clerk_token: str


async def _fetch_jwks() -> dict[str, Any]:
    global _jwks_cache
    if _jwks_cache:
        return _jwks_cache
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(CLERK_JWKS_URL)
        resp.raise_for_status()
        _jwks_cache = resp.json()
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

        return jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
    except JWTError as exc:
        logger.warning("Clerk JWT verification failed: %s", exc)
        raise HTTPException(status_code=401, detail=f"Invalid Clerk token: {exc}")


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
    if not CLERK_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Clerk backend sync is disabled. Set CLERK_SECRET_KEY and CLERK_JWKS_URL "
                f"(backend API: {CLERK_BACKEND_API_URL})."
            ),
        )

    claims = await _verify_clerk_token(payload.clerk_token)

    clerk_user_id: str = claims.get("sub", "")
    email: Optional[str] = claims.get("email") or claims.get("email_address")
    phone: Optional[str] = claims.get("phone_number")
    first_name: str = claims.get("given_name") or claims.get("first_name") or "User"
    last_name: str = claims.get("family_name") or claims.get("last_name") or ""
    full_name: str = f"{first_name} {last_name}".strip()
    is_verified: bool = bool(
        claims.get("email_verified") or claims.get("phone_verified")
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
