from fastapi.testclient import TestClient

from app.main import app


def test_attachments_upload_list_get_delete_download():
    with TestClient(app) as client:
        # upload
        files = {"file": ("hello.txt", b"hello world", "text/plain")}
        data = {"title": "My file"}
        r = client.post("/user/attachments", files=files, data=data)
        assert r.status_code == 200

        att = r.json()
        att_id = att["id"]

        assert att["originalfilename"] == "hello.txt"
        assert att["contenttype"] == "text/plain"
        assert att["sizebytes"] == 11
        assert att["isdeleted"] is False
        assert "createdat" in att

        # list
        r = client.get("/user/attachments?limit=50&offset=0")
        assert r.status_code == 200
        payload = r.json()
        assert "items" in payload
        assert isinstance(payload["items"], list)

        # get
        r = client.get(f"/user/attachments/{att_id}")
        assert r.status_code == 200
        got = r.json()
        assert got["id"] == att_id

        # download
        r = client.get(f"/user/attachments/{att_id}/download")
        assert r.status_code == 200
        assert r.content == b"hello world"

        # delete
        r = client.delete(f"/user/attachments/{att_id}")
        assert r.status_code == 200
        deleted = r.json()
        assert deleted["success"] is True
