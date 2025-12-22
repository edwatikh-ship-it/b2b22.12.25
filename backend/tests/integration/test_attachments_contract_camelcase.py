from fastapi.testclient import TestClient

from app.main import app


def test_attachments_response_fields_match_contract():
    with TestClient(app) as client:
        files = {"file": ("tmp-attachment.txt", b"hello from test", "text/plain")}
        data = {"title": "tmp-attachment"}

        r = client.post("/user/attachments", files=files, data=data)
        assert r.status_code == 200
        att = r.json()

        # Contract keys (api-contracts.yaml) are lowercase without separators
        expected_keys = {
            "id",
            "title",
            "originalfilename",
            "contenttype",
            "sizebytes",
            "sha256",
            "storagekey",
            "isdeleted",
            "createdat",
        }
        assert expected_keys.issubset(set(att.keys()))
