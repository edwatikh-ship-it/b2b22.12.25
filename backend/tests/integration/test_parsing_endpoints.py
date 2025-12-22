"""
Integration tests for parsing endpoints.
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def mock_parser_client():
    """Mock ParserServiceClient for tests."""
    with patch("app.adapters.parser_client.ParserServiceClient") as mock_cls:
        client_instance = mock_cls.return_value
        client_instance.start_parse = AsyncMock(
            return_value={"task_id": "test-task-123", "message": "Started", "started_at": "2025-12-22T00:00:00Z"}
        )
        client_instance.get_results = AsyncMock(
            return_value={"status": "completed", "links": ["https://example.com", "https://test.com"]}
        )
        
        with patch("app.usecases.start_parsing.ParserServiceClient", return_value=client_instance):
            with patch("app.usecases.get_parsing_results.ParserServiceClient", return_value=client_instance):
                yield client_instance


def test_start_parsing_success(mock_parser_client):
    """Test POST /moderator/requests/{requestId}/start-parsing - success case."""
    with TestClient(app) as client:
        create_resp = client.post(
            "/user/requests",
            json={
                "title": "Test Request",
                "keys": [
                    {"pos": 1, "text": "test keyword", "qty": 10, "unit": "pcs"}
                ]
            }
        )
        assert create_resp.status_code == 200
        request_id = create_resp.json()["requestid"]

        response = client.post(
            f"/moderator/requests/{request_id}/start-parsing",
            json={"depth": 5, "source": "google"}
        )
        
        if response.status_code != 200:
            print(f"Error response: {response.json()}")
        assert response.status_code == 200
        data = response.json()
        assert "requestId" in data
        assert "runId" in data
        assert "status" in data
        assert data["requestId"] == request_id
        assert data["status"] in ["queued", "running"]


def test_start_parsing_request_not_found():
    """Test POST /moderator/requests/{requestId}/start-parsing - request not found."""
    with TestClient(app) as client:
        response = client.post(
            "/moderator/requests/99999/start-parsing",
            json={"depth": 5, "source": "google"}
        )
        
        assert response.status_code == 404


def test_start_parsing_validation_error():
    """Test POST /moderator/requests/{requestId}/start-parsing - validation error."""
    with TestClient(app) as client:
        response = client.post(
            "/moderator/requests/1/start-parsing",
            json={"depth": 100, "source": "invalid"}
        )
        
        assert response.status_code == 422


def test_list_parsing_runs():
    """Test GET /moderator/parsing-runs."""
    with TestClient(app) as client:
        response = client.get("/moderator/parsing-runs?limit=10&offset=0")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "limit" in data
        assert "offset" in data
        assert "total" in data
        assert isinstance(data["items"], list)


def test_get_parsing_run_detail_not_found():
    """Test GET /moderator/parsing-runs/{runId} - run not found."""
    with TestClient(app) as client:
        response = client.get("/moderator/parsing-runs/non-existent-run-id")
        
        assert response.status_code == 404


def test_get_parsing_run_detail_success(mock_parser_client):
    """Test GET /moderator/parsing-runs/{runId} - success case."""
    with TestClient(app) as client:
        create_resp = client.post(
            "/user/requests",
            json={
                "title": "Test Request",
                "keys": [
                    {"pos": 1, "text": "test keyword", "qty": 10, "unit": "pcs"}
                ]
            }
        )
        assert create_resp.status_code == 200
        request_id = create_resp.json()["requestid"]

        start_resp = client.post(
            f"/moderator/requests/{request_id}/start-parsing",
            json={"depth": 5, "source": "google"}
        )
        assert start_resp.status_code == 200
        run_id = start_resp.json()["runId"]

        response = client.get(f"/moderator/parsing-runs/{run_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "requestId" in data
        assert "runId" in data
        assert "results" in data
        assert isinstance(data["results"], list)
