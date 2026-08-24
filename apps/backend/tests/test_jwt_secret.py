"""Production must not sign JWTs with the source-controlled default secret (CAR-83)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from career_forge.config import settings
from career_forge.main import app

DEV_JWT_SECRET = "career-forge-dev-jwt-secret-change-me-32b+"


def test_production_startup_rejects_default_jwt_secret() -> None:
    settings.env = "production"
    settings.jwt_secret = DEV_JWT_SECRET

    with pytest.raises(RuntimeError, match="JWT_SECRET"):
        with TestClient(app):
            pass


def test_local_startup_allows_default_jwt_secret() -> None:
    settings.env = "local"
    settings.jwt_secret = DEV_JWT_SECRET

    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
