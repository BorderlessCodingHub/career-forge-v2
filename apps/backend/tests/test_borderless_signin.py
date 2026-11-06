"""The Borderless password proxy is retired. See test_borderless_oauth.py."""

from fastapi.testclient import TestClient


def test_borderless_password_signin_is_gone(raw_client: TestClient) -> None:
    response = raw_client.post(
        "/auth/signin",
        json={"email": "signin-gone@example.com", "password": "correct-password"},
    )
    assert response.status_code == 410
