from fastapi.testclient import TestClient

from app.main import app


def test_moderator_blacklist_domains_add():
    with TestClient(app) as client:
        r = client.post(
            "/moderator/blacklist/domains",
            json={"domain": "example.com", "comment": "pytest"},
        )
        assert r.status_code == 200


def test_moderator_blacklist_domains_list():
    with TestClient(app) as client:
        r = client.get("/moderator/blacklist/domains?limit=200")
        assert r.status_code == 200


def test_moderator_blacklist_domains_delete():
    with TestClient(app) as client:
        r = client.delete("/moderator/blacklist/domains/example.com")
        assert r.status_code == 200
