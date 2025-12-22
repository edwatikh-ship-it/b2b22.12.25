from fastapi.testclient import TestClient

from app.main import app


def _first_request_id(client: TestClient) -> int:
    r = client.get("/user/requests?limit=1&offset=0")
    assert r.status_code == 200, r.text
    data = r.json()
    assert (
        "items" in data and len(data["items"]) >= 1
    ), "Need at least one request in DB to run messaging tests"
    return data["items"][0]["id"]


def test_send_returns_501():
    with TestClient(app) as client:
        rid = _first_request_id(client)
        r = client.post(
            f"/user/requests/{rid}/send",
            json={"subject": "t", "body": "b", "attachrequestfile": True, "attachmentids": []},
        )
        assert r.status_code == 501, r.text


def test_send_new_returns_501():
    with TestClient(app) as client:
        rid = _first_request_id(client)
        r = client.post(
            f"/user/requests/{rid}/send-new",
            json={"subject": "t", "body": "b", "attachrequestfile": True, "attachmentids": []},
        )
        assert r.status_code == 501, r.text


def test_messages_returns_501():
    with TestClient(app) as client:
        rid = _first_request_id(client)
        r = client.get(f"/user/requests/{rid}/messages?limit=1&offset=0")
        assert r.status_code == 501, r.text


def test_delete_message_returns_501():
    with TestClient(app) as client:
        r = client.delete("/user/messages/1")
        assert r.status_code == 501, r.text
