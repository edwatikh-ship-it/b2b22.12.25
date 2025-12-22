"""
Integration tests for Moderator LK extensions.
Tests for parsing logs, keywords base, and suppliers base.
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


def test_get_parsing_run_logs_not_found():
    """Test GET /moderator/parsing-runs/{runId}/logs - run not found."""
    with TestClient(app) as client:
        response = client.get("/moderator/parsing-runs/non-existent-run/logs")
        assert response.status_code == 404


def test_get_parsing_run_logs_success():
    """Test GET /moderator/parsing-runs/{runId}/logs - success case."""
    with TestClient(app) as client:
        # First create a request and start parsing
        create_resp = client.post(
            "/user/requests",
            json={
                "title": "Test Request",
                "keys": [{"pos": 1, "text": "test keyword", "qty": 10, "unit": "pcs"}]
            }
        )
        assert create_resp.status_code == 200
        request_id = create_resp.json()["requestid"]

        # Mock parser client
        with patch("app.usecases.start_parsing.ParserServiceClient") as mock_cls:
            client_instance = mock_cls.return_value
            client_instance.start_parse = AsyncMock(
                return_value={"task_id": "test-task", "message": "Started"}
            )
            
            start_resp = client.post(
                f"/moderator/requests/{request_id}/start-parsing",
                json={"depth": 5, "source": "google"}
            )
            assert start_resp.status_code == 200
            run_id = start_resp.json()["runId"]

        # Get logs
        response = client.get(f"/moderator/parsing-runs/{run_id}/logs")
        assert response.status_code == 200
        data = response.json()
        assert "runId" in data
        assert "events" in data
        assert isinstance(data["events"], list)
        assert data["runId"] == run_id
        
        # Check event structure
        if len(data["events"]) > 0:
            event = data["events"][0]
            assert "timestamp" in event
            assert "level" in event
            assert "message" in event
            assert event["level"] in ["info", "warn", "error"]


def test_list_keywords_empty():
    """Test GET /moderator/keywords - returns valid response structure."""
    with TestClient(app) as client:
        response = client.get("/moderator/keywords")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "limit" in data
        assert "offset" in data
        assert "total" in data
        assert isinstance(data["items"], list)
        assert data["limit"] == 50
        assert data["offset"] == 0
        assert data["total"] >= 0  # May have data from other tests


def test_list_keywords_with_filters():
    """Test GET /moderator/keywords with query parameters."""
    with TestClient(app) as client:
        response = client.get(
            "/moderator/keywords",
            params={
                "q": "test",
                "status": "pending",
                "limit": 20,
                "offset": 10,
                "sort": "keyword_desc"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 20
        assert data["offset"] == 10


def test_list_moderator_suppliers_empty():
    """Test GET /moderator/suppliers - returns valid response structure."""
    with TestClient(app) as client:
        response = client.get("/moderator/suppliers")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "limit" in data
        assert "offset" in data
        assert "total" in data
        assert isinstance(data["items"], list)
        assert data["limit"] == 50
        assert data["offset"] == 0
        assert data["total"] >= 0  # May have data from other tests


def test_list_moderator_suppliers_with_filters():
    """Test GET /moderator/suppliers with query parameters."""
    with TestClient(app) as client:
        response = client.get(
            "/moderator/suppliers",
            params={
                "q": "test",
                "type": "supplier",
                "limit": 20,
                "offset": 10,
                "sort": "name_desc"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 20
        assert data["offset"] == 10


def test_create_moderator_supplier():
    """Test POST /moderator/suppliers - create supplier."""
    with TestClient(app) as client:
        response = client.post(
            "/moderator/suppliers",
            json={
                "name": "Test Supplier",
                "inn": "1234567890",
                "email": "test@example.com",
                "domain": "example.com",
                "type": "supplier"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "name" in data
        assert "type" in data
        assert "createdAt" in data
        assert "updatedAt" in data
        assert data["name"] == "Test Supplier"
        assert data["type"] == "supplier"


def test_get_moderator_supplier():
    """Test GET /moderator/suppliers/{supplierId}."""
    with TestClient(app) as client:
        response = client.get("/moderator/suppliers/1")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "name" in data
        assert "type" in data
        assert data["id"] == 1


def test_get_moderator_supplier_not_found():
    """Test GET /moderator/suppliers/{supplierId} - not found."""
    with TestClient(app) as client:
        response = client.get("/moderator/suppliers/0")
        assert response.status_code == 404


def test_update_moderator_supplier():
    """Test PUT /moderator/suppliers/{supplierId}."""
    with TestClient(app) as client:
        response = client.put(
            "/moderator/suppliers/1",
            json={
                "name": "Updated Supplier",
                "type": "reseller"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "name" in data
        assert "updatedAt" in data
        assert data["id"] == 1


def test_update_moderator_supplier_not_found():
    """Test PUT /moderator/suppliers/{supplierId} - not found."""
    with TestClient(app) as client:
        response = client.put(
            "/moderator/suppliers/0",
            json={"name": "Test"}
        )
        assert response.status_code == 404
