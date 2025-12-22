from fastapi.testclient import TestClient

from app.main import app


def test_moderator_suppliers_list():
    """Test GET /moderator/suppliers returns valid response."""
    with TestClient(app) as client:
        r = client.get("/moderator/suppliers?q=bolt&limit=50&offset=0")
        assert r.status_code == 200
        data = r.json()
        assert "items" in data
        assert "total" in data


def test_moderator_suppliers_create():
    """Test POST /moderator/suppliers returns valid response."""
    with TestClient(app) as client:
        r = client.post(
            "/moderator/suppliers",
            json={
                "name": "ACME",
                "inn": "7707083893",
                "domain": "example.com",
                "email": "sales@example.com",
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert "id" in data
        assert "name" in data


def test_moderator_suppliers_get():
    """Test GET /moderator/suppliers/{id} returns valid response."""
    with TestClient(app) as client:
        r = client.get("/moderator/suppliers/1")
        assert r.status_code == 200
        data = r.json()
        assert "id" in data


def test_moderator_suppliers_update():
    """Test PUT /moderator/suppliers/{id} returns valid response."""
    with TestClient(app) as client:
        r = client.put("/moderator/suppliers/1", json={"name": "Updated"})
        assert r.status_code == 200
        data = r.json()
        assert "id" in data
