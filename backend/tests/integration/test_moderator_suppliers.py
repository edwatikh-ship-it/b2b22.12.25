from fastapi.testclient import TestClient

from app.main import app


def test_moderator_suppliers_list_not_implemented_yet():
    with TestClient(app) as client:
        r = client.get("/moderator/suppliers?q=bolt&limit=50&offset=0")
        assert r.status_code == 501


def test_moderator_suppliers_create_not_implemented_yet():
    with TestClient(app) as client:
        r = client.post(
            "/moderator/suppliers",
            json={
                "name": "ACME",
                "inn": "7707083893",
                "urloriginal": "https://example.com",
                "emails": ["sales@example.com"],
            },
        )
        assert r.status_code == 501


def test_moderator_suppliers_get_not_implemented_yet():
    with TestClient(app) as client:
        r = client.get("/moderator/suppliers/1")
        assert r.status_code == 501


def test_moderator_suppliers_update_not_implemented_yet():
    with TestClient(app) as client:
        r = client.put("/moderator/suppliers/1", json={"refreshchecko": False})
        assert r.status_code == 501
