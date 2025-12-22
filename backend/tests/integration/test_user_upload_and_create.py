from fastapi.testclient import TestClient

from app.main import app


def test_user_upload_and_create_not_implemented_yet():
    with TestClient(app) as client:
        files = {"file": ("hello.txt", b"hello", "text/plain")}
        r = client.post("/user/upload-and-create", files=files)
        assert r.status_code == 501
