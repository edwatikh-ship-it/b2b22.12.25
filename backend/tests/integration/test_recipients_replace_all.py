from fastapi.testclient import TestClient

from app.main import app


def _first_request_id(client: TestClient) -> int:
    r = client.get("/user/requests?limit=1&offset=0")
    assert r.status_code == 200, r.text
    data = r.json()
    assert "items" in data and len(data["items"]) >= 1, "Need at least one request in DB"
    return int(data["items"][0]["id"])


def test_recipients_replace_all_and_update_selected():
    with TestClient(app) as client:
        rid = _first_request_id(client)

        r1 = client.put(
            f"/user/requests/{rid}/recipients",
            json={
                "recipients": [
                    {"supplierid": 10, "selected": True},
                    {"supplierid": 20, "selected": True},
                ]
            },
        )
        assert r1.status_code == 200, r1.text
        assert r1.json()["recipients"] == [
            {"supplierid": 10, "selected": True},
            {"supplierid": 20, "selected": True},
        ]

        r2 = client.put(
            f"/user/requests/{rid}/recipients",
            json={
                "recipients": [
                    {"supplierid": 10, "selected": True},
                    {"supplierid": 20, "selected": False},
                ]
            },
        )
        assert r2.status_code == 200, r2.text
        assert r2.json()["recipients"] == [
            {"supplierid": 10, "selected": True},
            {"supplierid": 20, "selected": False},
        ]

        # replace-all removes missing supplierid=20 completely
        r3 = client.put(
            f"/user/requests/{rid}/recipients",
            json={"recipients": [{"supplierid": 10, "selected": True}]},
        )
        assert r3.status_code == 200, r3.text
        assert r3.json()["recipients"] == [{"supplierid": 10, "selected": True}]
