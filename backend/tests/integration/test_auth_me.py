from fastapi.testclient import TestClient

from app.main import app


def test_auth_me_requires_auth_401():
    with TestClient(app) as client:
        r = client.get("/auth/me")
        assert r.status_code == 401


def test_auth_me_ok_contract_fields():
    with TestClient(app) as client:
        r = client.get("/auth/me", headers={"Authorization": "Bearer dev"})
        assert r.status_code == 200, r.text
        body = r.json()
        assert isinstance(body.get("id"), int)
        assert isinstance(body.get("email"), str) and "@" in body["email"]
        assert body.get("emailpolicy") in ("appendonly", "allowdelete")
        assert isinstance(body.get("createdat"), str) and "T" in body["createdat"]
