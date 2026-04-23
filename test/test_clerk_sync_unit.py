import asyncio

import pytest
from fastapi import HTTPException

from core.auth_models import AuthMethod
from routes import clerk_sync


def test_clerk_strategy_google_account_maps_to_clerk_google() -> None:
    claims = {"external_accounts": [{"provider": "google"}]}
    assert clerk_sync._clerk_strategy_to_auth_method(claims) == AuthMethod.CLERK_GOOGLE


def test_clerk_strategy_phone_only_maps_to_clerk_phone() -> None:
    claims = {"phone_number": "+919999999999"}
    assert clerk_sync._clerk_strategy_to_auth_method(claims) == AuthMethod.CLERK_PHONE


def test_clerk_strategy_default_maps_to_clerk() -> None:
    claims = {"email": "user@example.com"}
    assert clerk_sync._clerk_strategy_to_auth_method(claims) == AuthMethod.CLERK


def test_verify_clerk_token_uses_matching_jwk(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_fetch_jwks() -> dict:
        return {
            "keys": [
                {
                    "kid": "kid-123",
                    "kty": "RSA",
                    "n": "abc",
                    "e": "AQAB",
                }
            ]
        }

    monkeypatch.setattr(clerk_sync, "_fetch_jwks", fake_fetch_jwks)
    monkeypatch.setattr(
        clerk_sync.jwt, "get_unverified_header", lambda _: {"kid": "kid-123"}
    )

    called: dict = {}

    def fake_decode(token, rsa_key, algorithms, options):
        called["token"] = token
        called["kid"] = rsa_key.get("kid")
        called["algorithms"] = algorithms
        called["options"] = options
        return {"sub": "user_123", "email": "citizen@example.com"}

    monkeypatch.setattr(clerk_sync.jwt, "decode", fake_decode)

    claims = asyncio.run(clerk_sync._verify_clerk_token("token-abc"))

    assert claims["sub"] == "user_123"
    assert called["token"] == "token-abc"
    assert called["kid"] == "kid-123"
    assert called["algorithms"] == ["RS256"]
    assert called["options"] == {"verify_aud": False}


def test_verify_clerk_token_raises_when_signing_key_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_fetch_jwks() -> dict:
        return {"keys": [{"kid": "some-other-kid"}]}

    monkeypatch.setattr(clerk_sync, "_fetch_jwks", fake_fetch_jwks)
    monkeypatch.setattr(
        clerk_sync.jwt, "get_unverified_header", lambda _: {"kid": "kid-404"}
    )

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(clerk_sync._verify_clerk_token("token-abc"))

    assert exc_info.value.status_code == 401
    assert "signing key" in str(exc_info.value.detail).lower()
