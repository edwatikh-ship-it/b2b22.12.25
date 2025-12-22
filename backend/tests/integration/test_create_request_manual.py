from fastapi.testclient import TestClient

from app.main import app


def test_create_request_manual_ok():
    with TestClient(app) as client:
        resp = client.post(
            "/user/requests",
            json={
                "title": "Test",
                "keys": [{"pos": 1, "text": "Bolt M8", "qty": 10, "unit": "pcs"}],
            },
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert isinstance(data["requestid"], int)
        assert data["status"] == "draft"
