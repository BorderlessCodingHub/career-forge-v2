"""Shared Borderless OAuth stand-in for API tests. No network."""

from __future__ import annotations

import time

import json

import jwt
from cryptography.hazmat.primitives.asymmetric import ed25519
from fastapi.testclient import TestClient
from jwt.algorithms import OKPAlgorithm

from career_forge.config import settings
from career_forge.services.borderless_oauth import (
    ISSUER,
    OAuthEndpoints,
    set_borderless_oauth_client,
)

CLIENT_ID = "cf-test-client"
CLIENT_SECRET = "cf-test-secret"
AUTHORIZE = "https://api.borderlesscoding.com/api/auth/oauth2/authorize"
TOKEN = "https://api.borderlesscoding.com/api/auth/oauth2/token"


class FakeBorderlessOAuth:
    def __init__(self) -> None:
        # The live issuer signs id tokens with EdDSA (Ed25519), not RS256.
        self.private = ed25519.Ed25519PrivateKey.generate()
        jwk = json.loads(OKPAlgorithm.to_jwk(self.private.public_key()))
        jwk["kid"] = "k1"
        jwk["alg"] = "EdDSA"
        self.jwk = jwk
        self.claims: dict = {}
        self.refresh_membership: str | None = None
        self.refresh_calls = 0
        self.invalid_grant = False
        self.last_form: dict[str, str] | None = None
        self.rotated_refresh = "refresh-rotated"

    def discovery(self) -> OAuthEndpoints:
        return OAuthEndpoints(
            authorization_endpoint=AUTHORIZE,
            token_endpoint=TOKEN,
            jwks_uri=f"{ISSUER}/.well-known/jwks.json",
        )

    def jwks(self) -> dict:
        return {"keys": [self.jwk]}

    def token(self, form: dict[str, str]) -> tuple[int, dict]:
        self.last_form = dict(form)
        if form.get("grant_type") == "refresh_token":
            self.refresh_calls += 1
            if self.invalid_grant:
                return 400, {"error": "invalid_grant"}
            membership = self.refresh_membership or self.claims.get("borderless_membership")
            claims = {**self.claims, "borderless_membership": membership, "nonce": "refresh"}
            return 200, {
                "access_token": "access-refreshed",
                "refresh_token": self.rotated_refresh,
                "id_token": self.sign(claims),
            }
        return 200, {
            "access_token": "access-code",
            "refresh_token": "refresh-1",
            "id_token": self.sign(self.claims),
        }

    def sign(self, claims: dict) -> str:
        token = jwt.encode(
            claims,
            self.private,
            algorithm="EdDSA",
            headers={"kid": "k1"},
        )
        return token if isinstance(token, str) else token.decode()


def enable_oauth() -> None:
    settings.identity_method = "borderless_password"
    settings.borderless_oauth_client_id = CLIENT_ID
    settings.borderless_oauth_client_secret = CLIENT_SECRET


def sign_in_with_borderless(
    raw_client: TestClient,
    *,
    email: str,
    sub: str,
    membership: str = "BASE",
    email_verified: bool = True,
    name: str = "Ada Lovelace",
) -> tuple[object, FakeBorderlessOAuth]:
    enable_oauth()
    fake = FakeBorderlessOAuth()
    set_borderless_oauth_client(fake)
    start = raw_client.get("/auth/borderless/start", follow_redirects=False)
    assert start.status_code == 302, start.text
    nonce = raw_client.cookies.get("cf_borderless_oauth_nonce")
    state = raw_client.cookies.get("cf_borderless_oauth_state")
    now = int(time.time())
    fake.claims = {
        "iss": ISSUER,
        "aud": CLIENT_ID,
        "sub": sub,
        "email": email,
        "email_verified": email_verified,
        "name": name,
        "nonce": nonce,
        "borderless_membership": membership,
        "iat": now,
        "exp": now + 3600,
    }
    response = raw_client.post(
        "/auth/borderless/callback",
        json={"code": "auth-code", "state": state},
    )
    return response, fake
