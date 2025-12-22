import re

from fastapi.testclient import TestClient

from app.main import app


def test_user_blacklist_inn_list_happy_path():
    headers = {"Authorization": "Bearer dev"}
    base = "/user/blacklist-inn"

    with TestClient(app) as client:
        r = client.post(base, headers=headers, json={"inn": "7707083893", "reason": "pytest"})
        assert r.status_code == 200, r.text
        assert r.json().get("success") is True

        r = client.get(f"{base}?limit=200", headers=headers)
        assert r.status_code == 200, r.text
        body = r.json()
        assert isinstance(body, dict) and "items" in body and isinstance(body["items"], list)

        if body["items"]:
            item = body["items"][0]
            assert item["inn"] == "7707083893"
            assert isinstance(item["id"], int)
            assert "createdat" in item and re.search(r"^\d{4}-\d{2}-\d{2}T", item["createdat"])
            assert "supplierid" in item and "suppliername" in item and "checkodata" in item

        r = client.delete(f"{base}/7707083893", headers=headers)
        assert r.status_code == 200, r.text
        assert r.json().get("success") is True
