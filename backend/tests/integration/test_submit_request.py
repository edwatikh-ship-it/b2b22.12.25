from fastapi.testclient import TestClient

from app.main import app


def test_submit_request_ok():
    with TestClient(app) as client:
        r = client.post(
            "/user/requests",
            json={"title": "SubmitMe", "keys": [{"pos": 1, "text": "Bolt"}]},
        )
        assert r.status_code == 200
        request_id = r.json()["requestid"]

        resp = client.post(f"/user/requests/{request_id}/submit")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["requestid"] == request_id
        assert data["newstatus"] == "confirmed"
        assert isinstance(data["matchedsuppliers"], int)


def test_submit_request_invalid_state_400():
    with TestClient(app) as client:
        r = client.post(
            "/user/requests",
            json={"title": "SubmitTwice", "keys": [{"pos": 1, "text": "Bolt"}]},
        )
        request_id = r.json()["requestid"]

        r1 = client.post(f"/user/requests/{request_id}/submit")
        assert r1.status_code == 200

        r2 = client.post(f"/user/requests/{request_id}/submit")
        assert r2.status_code == 400


def test_submit_request_404():
    with TestClient(app) as client:
        r = client.post("/user/requests/99999999/submit")
        assert r.status_code == 404
