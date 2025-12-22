from fastapi.testclient import TestClient

from app.main import app


def test_get_user_request_detail_ok():
    with TestClient(app) as client:
        # create
        r = client.post(
            "/user/requests",
            json={
                "title": "DetailTest",
                "keys": [{"pos": 1, "text": "Bolt M8", "qty": 10, "unit": "pcs"}],
            },
        )
        assert r.status_code == 200
        request_id = r.json()["requestid"]

        # detail
        resp = client.get(f"/user/requests/{request_id}")
        assert resp.status_code == 200

        data = resp.json()
        assert data["id"] == request_id
        assert data["status"] == "draft"
        assert isinstance(data["keys"], list)
        assert len(data["keys"]) == 1
        assert data["keys"][0]["pos"] == 1
        assert data["keys"][0]["rawtext"] == "Bolt M8"


def test_get_user_request_detail_404():
    with TestClient(app) as client:
        resp = client.get("/user/requests/99999999")
        assert resp.status_code == 404
