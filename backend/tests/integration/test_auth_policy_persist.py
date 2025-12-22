from fastapi.testclient import TestClient

from app.main import app


def test_auth_policy_persists_and_reflects_in_auth_me():
    with TestClient(app) as client:
        h = {"Authorization": "Bearer dev"}

        r = client.put("/auth/policy", headers=h, json={"emailpolicy": "allowdelete"})
        assert r.status_code == 200, r.text
        assert r.json()["emailpolicy"] == "allowdelete"

        r2 = client.get("/auth/me", headers=h)
        assert r2.status_code == 200, r2.text
        assert r2.json()["emailpolicy"] == "allowdelete"
