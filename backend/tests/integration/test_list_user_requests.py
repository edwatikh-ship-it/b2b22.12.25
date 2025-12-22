from fastapi.testclient import TestClient

from app.main import app


def test_list_user_requests_ok():
    with TestClient(app) as client:
        resp = client.get("/user/requests?limit=50&offset=0")
        assert resp.status_code == 200

        data = resp.json()
        assert "items" in data
        assert data["limit"] == 50
        assert data["offset"] == 0
        assert isinstance(data["total"], int)
