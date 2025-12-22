from fastapi.testclient import TestClient

from app.main import app


def test_auth_policy_requires_bearer():
    with TestClient(app) as client:
        r = client.put("/auth/policy", json={"emailpolicy": "appendonly"})
        assert r.status_code == 401


def test_auth_policy_put_ok():
    with TestClient(app) as client:
        r = client.put(
            "/auth/policy",
            headers={"Authorization": "Bearer dev"},
            json={"emailpolicy": "appendonly"},
        )
        assert r.status_code == 200
        assert r.json()["emailpolicy"] == "appendonly"
