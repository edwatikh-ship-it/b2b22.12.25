from fastapi.testclient import TestClient

from app.main import app


def test_update_request_keys_ok():
    with TestClient(app) as client:
        # create
        r = client.post(
            "/user/requests",
            json={
                "title": "UpdKeys",
                "keys": [{"pos": 1, "text": "Bolt", "qty": 1, "unit": "pcs"}],
            },
        )
        assert r.status_code == 200
        request_id = r.json()["requestid"]

        # update keys
        resp = client.put(
            f"/user/requests/{request_id}/keys",
            json={"keys": [{"pos": 1, "text": "Nut M10", "qty": 5, "unit": "pcs"}]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == request_id
        assert len(data["keys"]) == 1
        assert data["keys"][0]["rawtext"] == "Nut M10"


def test_update_request_keys_404():
    with TestClient(app) as client:
        resp = client.put("/user/requests/99999999/keys", json={"keys": [{"pos": 1, "text": "X"}]})
        assert resp.status_code == 404
