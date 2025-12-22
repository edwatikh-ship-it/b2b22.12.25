from fastapi.testclient import TestClient

from app.main import app


def test_auth_google_oauth_start_not_implemented_yet():
    with TestClient(app) as client:
        r = client.get("/auth/oauth/google/start")
        assert r.status_code == 501


def test_auth_google_oauth_callback_not_implemented_yet():
    with TestClient(app) as client:
        r = client.get("/auth/oauth/google/callback?code=dev")
        assert r.status_code == 501
